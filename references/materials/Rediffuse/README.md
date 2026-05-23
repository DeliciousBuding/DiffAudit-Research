# Towards Black-Box Membership Inference Attack for Diffusion Models

This code presents a black-box membership inference attack (MIA) algorithm called **ReDiffuse**.

## DDPM

### Training the DDPM Model

We provide a dataset split, including `DDPM/CIFAR10_train_ratio0.5.npz` and `DDPM/TINY-IN_train_ratio0.5.npz`. To train the DDPM, place the `cifar10`, `cifar100`, `stl10`, and `tiny-imagenet` datasets into `DDPM/data/pytorch`. You can also modify the dataset directory by changing the path in the `main.get_dataset` function and `dataset_utils.load_member_data`. The log directory can be updated by modifying `FLAGS.logdir` in `main.py`. Additionally, use `FLAGS.dataset` to select the desired dataset.

To start training the DDPM, run the following command:
```bash
cd DDPM
python main.py
```

### Attacking the DDPM Model

To execute an attack, run the following command:
```bash
cd DDPM
python micro_attack.py 
```

Parameters:

`--checkpoint`: The path to the saved model checkpoint.
`--dataset`: The dataset to attack, which can be `cifar10`, `cifar100`, `stl10`, or `TINY-IN`.
`--attacker_name`: The attack method. Options include `naive` for loss-based attack, `SecMI` for SecMI attack, `PIA` for PIA, `PIAN` for PIAN, and `Denoise` for the ReDiffuse attack algorithm.

## Diffusion Transformer

We conduct experiments on the Diffusion Transformer model based on the following repository: https://github.com/facebookresearch/DiT.

### Training the Diffusion Transformer

Use the command below to train the Diffusion Transformer:
```bash
cd dit
torchrun --nnodes=1 --nproc_per_node=8 train.py --model DiT-XL/2 --data-path <your_imagenet_data_path>
```

### Attacking the Diffusion Transformer

For ReDiffuse and baseline attacks, use the following command:
```bash
cd dit
python mia.py 
```

Parameters:

`--mia_type`: The attack method. Options include `naive` for loss-based attack, `secmi` for SecMI attack, `pia` for PIA, `pian` for PIAN, and `denoise` for the ReDiffuse attack algorithm.

## Stable Diffusion

We conduct experiments on the original Stable Diffusion model (stable-diffusion-v1-5) provided by Huggingface, without any additional fine-tuning or modifications.

### Attacking Stable Diffusion

For the ReDiffuse attack, run the following command:
```bash
cd stable_diffusion
python stable_attack.py
```







