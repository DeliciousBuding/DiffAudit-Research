from diffusers import StableDiffusionPipeline
import torch
from typing import Optional, Union, Dict, Any, List, Type
import components
from pytorch_lightning import seed_everything
import logging
from rich.logging import RichHandler
from rich.progress import track
from itertools import chain
import fire
import numpy as np
from dataset import load_member_data
from collections import defaultdict
from torchmetrics.classification import BinaryAUROC, BinaryROC
import matplotlib.pyplot as plt
import pynvml
import copy
from sklearn import metrics
import resnet
from torchvision.utils import save_image

def found_device():
    default_device=0
    default_memory_threshold=500
    pynvml.nvmlInit()
    while True:
        handle=pynvml.nvmlDeviceGetHandleByIndex(default_device)
        meminfo=pynvml.nvmlDeviceGetMemoryInfo(handle)
        used=meminfo.used/1024**2
        if used<default_memory_threshold:
            break
        else:
            default_device+=1
        if default_device>=8:
            default_device=0
            default_memory_threshold+=1000
    pynvml.nvmlShutdown()
    return str(default_device)


device_str = 'cuda:' + found_device() if torch.cuda.is_available() else 'cpu'
DEVICE = torch.device(device_str)

class EpsGetter(components.EpsGetter):
    def __call__(self, xt: torch.Tensor, condition: torch.Tensor = None, noise_level=None, t: int = None) -> torch.Tensor:
        # t = torch.ones([xt.shape[0]], device=xt.device).long() * t
        return self.model(t, condition, latents=xt)


class MyStableDiffusionPipeline(StableDiffusionPipeline):
    @torch.no_grad()
    def prepare_latent(self, img):
        latents = self.vae.encode(img).latent_dist.sample()
        latents = latents * 0.18215
        return latents

    @torch.no_grad()
    def encode_input_prompt(self, prompt, do_classifier_free_guidance=True):
        text_encoder_lora_scale = None
        prompt_embeds = self._encode_prompt(
            prompt,
            DEVICE,
            1,
            do_classifier_free_guidance,
            None,
            prompt_embeds=None,
            negative_prompt_embeds=None,
            lora_scale=text_encoder_lora_scale,
        )
        return prompt_embeds

    @torch.no_grad()
    def __call__(
        self,
        t,
        prompt_embeds,
        prompt: Union[str, List[str]] = None,
        height: Optional[int] = None,
        width: Optional[int] = None,
        guidance_scale: float = 7.5,
        negative_prompt: Optional[Union[str, List[str]]] = None,
        latents: Optional[torch.FloatTensor] = None,
        negative_prompt_embeds: Optional[torch.FloatTensor] = None,
        callback_steps: int = 1,
        cross_attention_kwargs: Optional[Dict[str, Any]] = None,
    ):
        # 0. Default height and width to unet
        height = height or self.unet.config.sample_size * self.vae_scale_factor
        width = width or self.unet.config.sample_size * self.vae_scale_factor

        # 1. Check inputs. Raise error if not correct
        self.check_inputs(
            prompt, height, width, callback_steps, negative_prompt, prompt_embeds, negative_prompt_embeds
        )

        do_classifier_free_guidance = guidance_scale > 1.0

        # 7. Denoising loop
        # expand the latents if we are doing classifier free guidance
        latent_model_input = torch.cat([latents] * 2) if do_classifier_free_guidance else latents

        # predict the noise residual
        noise_pred = self.unet(
            latent_model_input,
            t,
            encoder_hidden_states=prompt_embeds,
            cross_attention_kwargs=cross_attention_kwargs,
            return_dict=False,
        )[0]

        # perform guidance
        if do_classifier_free_guidance:
            noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
            noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)

        return noise_pred

    def get_image(self, latents):
        image = self.vae.decode(latents / self.vae.config.scaling_factor, return_dict=False)[0]

        do_denormalize = [True] * image.shape[0]

        image = self.image_processor.postprocess(image, output_type="pil", do_denormalize=do_denormalize)
        return image

from skimage.metrics import structural_similarity as ssim
from PIL import Image

def calculate_ssim(image1, image2):
  
    image1 = np.array(image1.convert('L'))
    image2 = np.array(image2.convert('L'))
    

    ssim_value = ssim(image1, image2, data_range=image2.max() - image2.min())
    
    return ssim_value

def get_FLAGS():

    def FLAGS(x): return x
    FLAGS.T = 1000
    FLAGS.ch = 128
    FLAGS.ch_mult = [1, 2, 2, 2]
    FLAGS.attn = [1]
    FLAGS.num_res_blocks = 2
    FLAGS.dropout = 0.1
    FLAGS.beta_1 = 0.00085
    FLAGS.beta_T = 0.012

    return FLAGS


attackers: Dict[str, Type[components.DDIMAttacker]] = {
    "SecMI": components.SecMIAttacker,
    "PIA": components.PIA,
    "Naive": components.NaiveAttacker,
    "PIAN": components.PIAN,
    "Denoise": components.DenoiseAttacker
}

def nns_attack(device, members_diffusion, members_sample, nonmembers_diffusion, nonmembers_sample, train_portion=0.5):
    n_epoch = 15
    lr = 0.001
    batch_size = 128
    # model training
    train_loader, test_loader, num_timestep = split_nn_datasets(members_diffusion, members_sample, nonmembers_diffusion, nonmembers_sample, train_portion=train_portion,
                                                                batch_size=batch_size)
    # initialize NNs
    model = resnet.ResNet18(num_channels=4 * num_timestep * 1, num_classes=1).to(device)
    optim = torch.optim.SGD(model.parameters(), lr=lr, momentum=0.9, weight_decay=5e-4)

    test_acc_best_ckpt = None
    test_acc_best = 0
    for epoch in range(n_epoch):
        train_loss, train_acc = nn_train(device, epoch, model, optim, train_loader)
        test_loss, test_acc = nn_eval(device, model, test_loader)
        if test_acc > test_acc_best:
            test_acc_best_ckpt = copy.deepcopy(model.state_dict())

    
    # resume best ckpt
    model.load_state_dict(test_acc_best_ckpt)
    
    model.eval()
    member_scores = []
    nonmember_scores = []

    with torch.no_grad():
        for batch_idx, (data, label) in enumerate(test_loader):
            logits = model(data.to(device))
           
            logits_cpu = logits.detach().cpu()
            member_scores.append(logits_cpu[label == 1])
            nonmember_scores.append(logits_cpu[label == 0])

   
    member_scores = torch.cat(member_scores).reshape(-1)
    nonmember_scores = torch.cat(nonmember_scores).reshape(-1)
    return member_scores, nonmember_scores, model



def nn_train(device, epoch, model, optimizer, data_loader):
    model.train()

    mean_loss = 0
    total = 0
    acc = 0

    for batch_idx, (data, label) in enumerate(data_loader):
        data = data.to(device)
        label = label.to(device).reshape(-1, 1)
        logit = model(data)
        loss = ((logit - label) ** 2).mean()
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        mean_loss += loss.item()
        total += data.size(0)

        logit[logit >= 0.5] = 1
        logit[logit < 0.5] = 0
        acc += (logit == label).sum()

    mean_loss /= len(data_loader)
    print(f'Epoch: {epoch} \t Loss: {mean_loss:.4f} \t Acc: {acc / total:.4f} \t')
    return mean_loss, acc / total

def nn_eval(device, model, data_loader):
    model.eval()

    mean_loss = 0
    total = 0
    acc = 0

    for batch_idx, (data, label) in enumerate(data_loader):
        data, label = data.to(device), label.to(device).reshape(-1, 1)
        logit = model(data)
        loss = ((logit - label) ** 2).mean()

        mean_loss += loss.item()
        total += data.size(0)

        logit[logit >= 0.5] = 1
        logit[logit < 0.5] = 0

        acc += (logit == label).sum()

    mean_loss /= len(data_loader)
    print(f'Test: \t Loss: {mean_loss:.4f} \t Acc: {acc / total:.4f} \t')
    return mean_loss, acc / total

class MIDataset():

    def __init__(self, member_data, nonmember_data, member_label, nonmember_label):
        self.data = torch.concat([member_data, nonmember_data])
        self.label = torch.concat([member_label, nonmember_label]).reshape(-1)

    def __len__(self):
        return self.data.size(0)

    def __getitem__(self, item):
        data = self.data[item]
        return data, self.label[item]
    
def split_nn_datasets(member_diffusion, member_sample, nonmember_diffusion, nonmember_sample, train_portion=0.2, batch_size=128):
    # split training and testing
    # train num
    member_concat = (member_diffusion - member_sample).abs() ** 1
    nonmember_concat = (nonmember_diffusion - nonmember_sample).abs() ** 1
    
    # train num
    num_train = int(member_concat.size(0) * train_portion)
    # split
    train_member_concat = member_concat[:num_train]
    train_member_label = torch.ones(train_member_concat.size(0))
    train_nonmember_concat = nonmember_concat[:num_train]
    train_nonmember_label = torch.zeros(train_nonmember_concat.size(0))
    test_member_concat = member_concat[num_train:]
    test_member_label = torch.ones(test_member_concat.size(0))
    test_nonmember_concat = nonmember_concat[num_train:]
    test_nonmember_label = torch.zeros(test_nonmember_concat.size(0))

    # datasets
    if num_train == 0:
        train_dataset = None
        train_loader = None
    else:
        train_dataset = MIDataset(train_member_concat, train_nonmember_concat, train_member_label,
                                  train_nonmember_label)
        train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    test_dataset = MIDataset(test_member_concat, test_nonmember_concat, test_member_label, test_nonmember_label)
    # dataloader
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    return train_loader, test_loader, 1

def roc(member_scores, nonmember_scores, n_points=1000):
    max_asr = 0
    max_threshold = 0

    min_conf = min(member_scores.min(), nonmember_scores.min()).item()
    max_conf = max(member_scores.max(), nonmember_scores.max()).item()

    FPR_list = []
    TPR_list = []

    for threshold in torch.arange(min_conf, max_conf, (max_conf - min_conf) / n_points):
        TP = (member_scores <= threshold).sum()
        TN = (nonmember_scores > threshold).sum()
        FP = (nonmember_scores <= threshold).sum()
        FN = (member_scores > threshold).sum()

        TPR = TP / (TP + FN)
        FPR = FP / (FP + TN)

        ASR = (TP + TN) / (TP + TN + FP + FN)

        TPR_list.append(TPR.item())
        FPR_list.append(FPR.item())

        if ASR > max_asr:
            max_asr = ASR
            max_threshold = threshold

    FPR_list = np.asarray(FPR_list)
    TPR_list = np.asarray(TPR_list)
    auc = metrics.auc(FPR_list, TPR_list)
    return auc, max_asr, torch.from_numpy(FPR_list), torch.from_numpy(TPR_list), max_threshold


def plot_scores_distribution(member_scores, nonmember_scores, flag):
    if torch.is_tensor(member_scores):
        member_scores = member_scores.cpu().numpy()
    if torch.is_tensor(nonmember_scores):
        nonmember_scores = nonmember_scores.cpu().numpy()
    
    all_scores = np.concatenate((member_scores, nonmember_scores))
    min_score = np.min(all_scores)
    max_score = np.max(all_scores)

    bins = np.linspace(min_score, max_score, 50)

    print('Member Scores: mean: {:.4f}, std: {:.4f}'.format(np.mean(member_scores), np.std(member_scores)))
    print('Non-Member Scores: mean: {:.4f}, std: {:.4f}'.format(np.mean(nonmember_scores), np.std(nonmember_scores)))

    plt.figure(figsize=(10, 8))
   
    plt.hist(member_scores, bins=bins, alpha=0.5, label='Member Scores')
    
   
    plt.hist(nonmember_scores, bins=bins, alpha=0.5, label='Non-Member Scores')
    
    plt.legend(loc='upper right', fontsize=18)
    
   
    plt.title('Distribution of Member vs Non-Member Scores', fontsize=18)
    plt.xlabel('Scores', fontsize=18)
    plt.ylabel('Frequency', fontsize=18)
    plt.tick_params(axis='both', which='major', labelsize=16)
    
    if flag == 0:
        plt.savefig('stats.png')
    else:
        plt.savefig('nns.png')

def main(attacker_name="Denoise",
         dataset="draw_figure",
         checkpoint="runwayml/stable-diffusion-v1-5",
         attack_num=1, interval=200,
         save_logger=None,
         seed=3,k=100,average=1):
    seed_everything(seed)

    FLAGS = get_FLAGS()

    logger = logging.getLogger()
    logger.disabled = True if save_logger else False
    logger.setLevel(logging.INFO)
    logger.addHandler(RichHandler())

    logger.info("loading model...")
    model = MyStableDiffusionPipeline.from_pretrained(checkpoint, torch_dtype=torch.float32)
    model = model.to(DEVICE)
    # model.eval()

    def attacker_wrapper(attack):
        def wrapper(x, condition=None):
            x = model.prepare_latent(x)
            if 'none' in dataset:
                condition = ['none'] * len(condition)
            if condition is not None:
                condition = model.encode_input_prompt(condition)
            return attack(x, condition)

        return wrapper

    logger.info("loading dataset...")
    _, _, train_loader, test_loader = load_member_data(dataset_name=dataset, batch_size=4)

    attacker = attackers[attacker_name](
        torch.from_numpy(np.linspace(FLAGS.beta_1, FLAGS.beta_T, FLAGS.T)).to(DEVICE), interval, average, attack_num, k, EpsGetter(model), lambda x: x * 2 - 1)
    attacker = attacker_wrapper(attacker)

    logger.info("attack start...")
    members, nonmembers = [], []
    
    with torch.no_grad():
        for member, nonmember in track(zip(train_loader, chain(*([test_loader]))), total=len(test_loader)):
            member_condition, nonmenmer_condition = member[1], nonmember[1]
            member, nonmember = member[0].to(DEVICE), nonmember[0].to(DEVICE)
           
            epsilon = torch.randn_like(member[0])
            noise_level = torch.cumprod(1 - torch.from_numpy(np.linspace(FLAGS.beta_1, FLAGS.beta_T, FLAGS.T)).to(DEVICE), dim=0).float()
            alphas_t_target = noise_level[interval]
           
            prime_member = alphas_t_target.sqrt() * member[0] + (1 - alphas_t_target).sqrt() * epsilon
            epsilon = torch.randn_like(nonmember[0])
            prime_nonmember = alphas_t_target.sqrt() * nonmember[0] + (1 - alphas_t_target).sqrt() * epsilon
            save_image(prime_member, 'prime_member.png')
            save_image(prime_nonmember, 'prime_nonmember.png')
            intermediate_reverse_member, intermediate_denoise_member = attacker(member, member_condition)
            intermediate_reverse_nonmember, intermediate_denoise_nonmember = attacker(nonmember, nonmenmer_condition)
            prime_member = intermediate_reverse_member[0]
            prime_member = (prime_member + 1) / 2
            prime_member = model.get_image(prime_member)
            reconstruction_member = intermediate_denoise_member[0]
            reconstruction_member = (reconstruction_member + 1) / 2
            reconstruction_member = model.get_image(reconstruction_member)
            reconstruction_member[0].save('reconstruction_member.png')
            prime_nonmember = intermediate_reverse_nonmember[0]
            prime_nonmember = (prime_nonmember + 1) / 2
            prime_nonmember = model.get_image(prime_nonmember)
            reconstruction_nonmember = intermediate_denoise_nonmember[0]
            reconstruction_nonmember = (reconstruction_nonmember + 1) / 2
            reconstruction_nonmember = model.get_image(reconstruction_nonmember)
            reconstruction_nonmember[0].save('reconstruction_nonmember.png')
            
            # calculate the distance
            for i in range(len(prime_member)):
                dist = calculate_ssim(prime_member[i], reconstruction_member[i])
                members.append(dist)
            for i in range(len(prime_nonmember)):
                dist = calculate_ssim(prime_nonmember[i], reconstruction_nonmember[i])
                nonmembers.append(dist)
           
    member = torch.tensor(members)
    nonmember = torch.tensor(nonmembers)
    member *= -1
    nonmember *= -1
    plot_scores_distribution(member, nonmember, 0)
    auc, asr, fpr_list, tpr_list, threshold = roc(member, nonmember, n_points=2000)
    
    # TPR @ 1% FPR
    asr = asr.item()
    tpr_1_fpr = tpr_list[(fpr_list - 0.01).abs().argmin(dim=0)]
    tpr_1_fpr = tpr_1_fpr.item()
    # TPR @ 0.1% FPR
    tpr_01_fpr = tpr_list[(fpr_list - 0.001).abs().argmin(dim=0)]
    tpr_01_fpr = tpr_01_fpr.item()
    print('AUC:', auc)
    print('ASR:', asr)
    print('TPR @ 1% FPR:', tpr_1_fpr)
    print('TPR @ 0.1% FPR:', tpr_01_fpr)
    result_dir = 'result.csv'
    f = open(result_dir, 'a')
    f.write(dataset + ',' + attacker_name + ',' + str(attack_num) + ',' + str(interval) + ', stats' + ',' + str(k) + ',' + str(average))
    f.write(',' + str(auc) + ',' + str(asr) + ',' + str(tpr_1_fpr) + ',' + str(tpr_01_fpr) + '\n')
     
if __name__ == '__main__':
    fire.Fire(main)
