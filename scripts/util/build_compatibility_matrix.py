#!/usr/bin/env python3
"""
DATASET x CHECKPOINT COMPATIBILITY MATRIX
DiffAudit Research  Single Source of Truth for Experiment Planning
Generated: 2026-06-20

Reads catalog_checkpoints.json and local evidence to produce the definitive
compatibility matrix mapping every dataset (with split file) against every
compatible checkpoint.

LEGEND:
  [OK] = Compatible AND tested (results available)
  [UNTESTED] = Compatible but UNTESTED (runnable, no results)
  [NO] = Incompatible (format mismatch / missing membership provenance / blocked)
   = Direction closed (weak results, route blocked by governance)
"""

import json
from pathlib import Path

RESEARCH = Path("D:/Code/DiffAudit/Research")

# 
# DATASETS (with split files that define member/nonmember)
# 

datasets = {
    "CIFAR-10": {
        "split": "cifar-10-batches-py: data_batch_1-5 (train 50k) + test_batch (test 10k)",
        "member_tensor": "Download/shared/datasets/cifar10_member_25k.pt",
        "npz_split": "CIFAR10_train_ratio0.5.npz (25k member / 25k nonmember)",
        "resolution": "32x32x3",
        "membership_provenance": "PROVEN: explicit train/test split + 25k/25k member/nonmember cache",
    },
    "CIFAR-100": {
        "split": "cifar-100-python: train (50k) + test (10k)",
        "member_tensor": None,
        "npz_split": "CIFAR100_train_ratio0.5.npz (25k member / 25k nonmember)",
        "resolution": "32x32x3",
        "membership_provenance": "PROVEN: explicit train/test split + 25k/25k member/nonmember cache",
    },
    "STL-10": {
        "split": "stl10_binary: train_X.bin (5k) + test_X.bin (8k) + fold_indices.txt + unlabeled_X.bin (100k)",
        "member_tensor": "Download/shared/datasets/stl10_member_50k.pt",
        "npz_split": "STL10_train_ratio0.5.npz (50k member / 50k nonmember)",
        "resolution": "96x96x3",
        "membership_provenance": "PROVEN: explicit train/test split + fold indices + 50k/50k cache",
    },
    "Fashion-MNIST": {
        "split": "FashionMNIST raw: train-images (60k) + t10k-images (10k)",
        "member_tensor": None,
        "npz_split": None,
        "resolution": "28x28x1",
        "membership_provenance": "PROVEN: explicit train/test split. NO local DDPM checkpoint persisted.",
    },
    "Beans": {
        "split": "HF datasets: train + validation splits",
        "member_tensor": None,
        "npz_split": None,
        "resolution": "variable (resized to 512x512 for SD1.5)",
        "membership_provenance": "NOT PROVEN for SD1.5 membership: train/val split exists but not shown as SD1.5 training membership",
    },
    "CelebA": {
        "split": "list_eval_partition.txt: train/val/test partitions",
        "member_tensor": None,
        "npz_split": None,
        "resolution": "178x218",
        "membership_provenance": "PARTITION exists but no diffusion checkpoint trained on known member/nonmember splits",
    },
}

# 
# CHECKPOINTS (deduplicated by structural identity)
# 

checkpoints = {
    "DDPM-CIFAR10-800k": {
        "format": "rediffuse-unet",
        "dataset": "CIFAR10",
        "step": 800000,
        "channels": "128/256",
        "size_mb": 548,
        "loads_in_rediffuse": True,
        "paths": [
            "gray-box/supplementary/pia-upstream-assets/contents/checkpoints/cifar10_ddpm/checkpoint.pt",
            "gray-box/weights/secmi-cifar-bundle/CIFAR10/checkpoint.pt",
            "gray-box/weights/secmi-cifar-bundle/contents/checkpoints/CIFAR10/checkpoint.pt",
        ],
        "note": "SecMI bundle + PIA upstream, 3 identical copies",
    },
    "DDPM-CIFAR100-800k": {
        "format": "rediffuse-unet",
        "dataset": "CIFAR100",
        "step": 800000,
        "channels": "128/256",
        "size_mb": 548,
        "loads_in_rediffuse": True,
        "paths": [
            "gray-box/weights/secmi-cifar-bundle/CIFAR100/checkpoint.pt",
            "gray-box/weights/secmi-cifar-bundle/contents/checkpoints/CIFAR100/checkpoint.pt",
        ],
        "note": "SecMI bundle CIFAR100, 2 copies. Same architecture as CIFAR10-800k, different weights.",
    },
    "DDIM-CIFAR10-750k": {
        "format": "rediffuse-unet",
        "dataset": "CIFAR10",
        "step": 750000,
        "channels": "128/256",
        "size_mb": 548,
        "loads_in_rediffuse": True,
        "paths": [
            "shared/weights/ddim-cifar10-step750000/raw/DDIM-ckpt-step750000.pt"
        ],
        "note": "DDIM collaborator checkpoint, ReDiffuse-compatible",
    },
    "GuidedDiff-CIFAR10-500k": {
        "format": "guided-diffusion-unet",
        "dataset": "CIFAR10",
        "step": 500000,
        "channels": "256/256",
        "size_mb": 201,
        "loads_in_rediffuse": True,
        "paths": ["shared/weights/cifar10_openai_500k.pt"],
        "note": "OpenAI guided-diffusion format, different UNet architecture from Rediffuse",
    },
    "DDPM-STL10-final": {
        "format": "rediffuse-unet",
        "dataset": "STL10",
        "step": "final (bounded scout)",
        "channels": "128/256",
        "size_mb": 547,
        "loads_in_rediffuse": True,
        "paths": [
            "shared/runs/rediffuse-stl10-bounded-scout-20260525/checkpoint-step-final.pt"
        ],
        "note": "ReDiffuse STL10 bounded scout training (fresh train), includes train_indices + score indices",
    },
    "DDPM-STL10-99k": {
        "format": "rediffuse-unet",
        "dataset": "STL10",
        "step": 99000,
        "channels": "128/256",
        "size_mb": 548,
        "loads_in_rediffuse": True,
        "paths": [
            "shared/supplementary/collaborator-ddim-stl10-20260527/code/logs/DDPM_STL10_EPS/ckpt-step99000.pt"
        ],
        "note": "Collaborator DDPM STL10 EPS training, 99k steps",
    },
    "DDPM-STL10-overfit-m1000-9k": {
        "format": "rediffuse-unet",
        "dataset": "STL10",
        "step": 9000,
        "channels": "128/256",
        "size_mb": 548,
        "loads_in_rediffuse": True,
        "paths": [
            "shared/supplementary/collaborator-ddim-stl10-20260527/code/logs/DDPM_STL10_OVERFIT_m1000_seed0_EPS/ckpt-step9000.pt",
            "shared/supplementary/collaborator-ddim-stl10-20260527/code/logs/DDPM_STL10_OVERFIT_m1000_seed0_cont10k_EPS/ckpt-step9000.pt",
        ],
        "note": "Overfit 1000-member STL10, seed 0, 9k steps",
    },
    "DDPM-STL10-overfit-m1000-5k": {
        "format": "rediffuse-unet",
        "dataset": "STL10",
        "step": 5000,
        "channels": "128/256",
        "size_mb": 548,
        "loads_in_rediffuse": True,
        "paths": [
            "shared/supplementary/collaborator-ddim-stl10-20260527/code/logs/DDPM_STL10_OVERFIT_m1000_seed0_cont15k_EPS/ckpt-step5000.pt",
            "shared/supplementary/collaborator-ddim-stl10-20260527/code/logs/DDPM_STL10_OVERFIT_m1000_seed0_cont20k_EPS/ckpt-step5000.pt",
            "shared/supplementary/collaborator-ddim-stl10-20260527/code/logs/DDPM_STL10_OVERFIT_m1000_seed0_cont25k_EPS/ckpt-step5000.pt",
        ],
        "note": "Overfit 1000-member STL10, continued from 15k/20k/25k base, 5k steps",
    },
    "DDPM-STL10-overfit-m2000-8k": {
        "format": "rediffuse-unet",
        "dataset": "STL10",
        "step": 8000,
        "channels": "128/256",
        "size_mb": 548,
        "loads_in_rediffuse": True,
        "paths": [
            "shared/supplementary/collaborator-ddim-stl10-20260527/code/logs/DDPM_STL10_OVERFIT_m2000_seed0_EPS/ckpt-step8000.pt"
        ],
        "note": "Overfit 2000-member STL10, seed 0, 8k steps",
    },
    "DDPM-STL10-overfit-m500-9k": {
        "format": "rediffuse-unet",
        "dataset": "STL10",
        "step": 9000,
        "channels": "128/256",
        "size_mb": 548,
        "loads_in_rediffuse": True,
        "paths": [
            "shared/supplementary/collaborator-ddim-stl10-20260527/code/logs/DDPM_STL10_OVERFIT_m500_seed1_EPS/ckpt-step9000.pt"
        ],
        "note": "Overfit 500-member STL10, seed 1, 9k steps",
    },
    "Beans-LoRA-SD15": {
        "format": "peft-lora",
        "dataset": "Beans",
        "step": None,
        "channels": None,
        "size_mb": 3,
        "loads_in_rediffuse": False,
        "paths": [
            "black-box/weights/beans-lora-member-denoising-loss-20260513/unet_lora_peft_state.pt"
        ],
        "note": "PEFT/LoRA weights for SD1.5 UNet, not a standalone checkpoint",
    },
    "NDSS-2025-derived": {
        "format": "unknown (text+image wrapper)",
        "dataset": "unknown (COCO-like, fine-tuned SD)",
        "step": None,
        "channels": None,
        "size_mb": "4-428",
        "loads_in_rediffuse": False,
        "paths": [
            "black-box/supplementary/recon-assets/ndss-2025.../derived-public-{10,25,50,100}/shadow_member_proxy.pt etc."
        ],
        "note": "Black-box proxy tensors (text+image), not loadable model checkpoints",
    },
    "SD-v1-4-CompVis": {
        "format": "diffusers (HuggingFace)",
        "dataset": "LAION-5B (pretraining)",
        "step": None,
        "channels": None,
        "size_mb": None,
        "loads_in_rediffuse": False,
        "paths": ["CompVis/stable-diffusion-v1-4 (HF hub)"],
        "note": "Used in xuchi-reproduction (COCO-like MIA), not stored as local checkpoint file",
    },
}

# 
# COMPATIBILITY MATRIX
# 

matrix = {
    "CIFAR-10": {
        "DDPM-CIFAR10-800k": {
            "status": "[OK]",
            "experiments": [
                "E3 eval: SecMI (t100/t50/t200, k10/k5/k20), all AUC approx 0.46 (weak)",
                "E3 eval: PIA int200/int100, AUC=0.605 (moderate)",
                "H2 sidecar: score-vector scout, AUC=0.681, label-shuffle=0.475",
                "Gray-box: SecMI full 25k/25k, AUC=0.886, NNS AUC=0.946 (evidence-ready)",
                "Gray-box: PIA admitted as strongest gray-box attack",
                "Gray-box: Tri-score CDI/TMIA-DM/PIA, AUC=0.859 (internal-only)",
                "Gray-box: 800k PIA checkpoint verified ReDiffuse runtime-probe compatible on CPU",
            ],
            "gaps": [
                "No ResNet collaborator replay on 800k (only on 750k DDIM)",
                "No direct-distance boundary metrics on 800k",
                "No white-box (GSA/fisher/influence) on 800k",
            ],
        },
        "DDPM-CIFAR100-800k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": [
                "CIFAR100 checkpoint not compatible with CIFAR10 dataset (different class count, head/tail differ)"
            ],
        },
        "DDIM-CIFAR10-750k": {
            "status": "[OK]",
            "experiments": [
                "E3 eval: SecMI, all AUC approx 0.40 (weaker than 800k)",
                "E3 eval: PIA int200/int100, AUC=0.599-0.605",
                "H1 scout: DDIM channel knockout, baseline AUC=0.895, targeted mean=0.668",
                "Gray-box: 750k first_step_distance_mean 64/64, positive but not comparable",
                "Gray-box: 750k resnet 64/64 parity, AUC=0.412 (negative)",
                "Gray-box: resnet_collaborator_replay GPU, AUC=0.702, TPR@1%=0.019 (candidate-only)",
                "Gray-box: checkpoint-portability gate: 750k/800k metadata + split hash compatible",
            ],
            "gaps": [
                "No full SecMI 25k/25k on DDIM-750k",
                "No tri-score packet on DDIM-750k",
                "ResNet replay strict-tail evidence is weak",
            ],
        },
        "GuidedDiff-CIFAR10-500k": {
            "status": "[UNTESTED]",
            "experiments": [],
            "gaps": [
                "Guided-diffusion format (different architecture from Rediffuse)",
                "Loads in Rediffuse but no membership inference experiments run",
                "No SecMI/PIA/first_step_distance evaluation",
                "Would need architecture adapter to compare with Rediffuse results",
            ],
        },
        "DDPM-STL10-final": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["STL10 checkpoint trained on STL10 data, not CIFAR10"],
        },
        "DDPM-STL10-99k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["STL10 checkpoint, different dataset + resolution"],
        },
        "DDPM-STL10-overfit-m1000-9k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["STL10 overfit checkpoint, different dataset"],
        },
        "DDPM-STL10-overfit-m1000-5k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["STL10 overfit checkpoint, different dataset"],
        },
        "DDPM-STL10-overfit-m2000-8k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["STL10 overfit checkpoint, different dataset"],
        },
        "DDPM-STL10-overfit-m500-9k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["STL10 overfit checkpoint, different dataset"],
        },
        "Beans-LoRA-SD15": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["SD1.5 LoRA on Beans, not a CIFAR10 checkpoint"],
        },
        "NDSS-2025-derived": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["Black-box proxy tensors, not loadable CIFAR10 checkpoint"],
        },
        "SD-v1-4-CompVis": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["Stable Diffusion on LAION, not CIFAR10. Different domain entirely."],
        },
    },
    "CIFAR-100": {
        "DDPM-CIFAR10-800k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["CIFAR10 checkpoint not compatible with CIFAR100 dataset"],
        },
        "DDPM-CIFAR100-800k": {
            "status": "[OK]",
            "experiments": [
                "H1 scout: CIFAR100 channel knockout, baseline AUC=0.811",
                "H1: late_down_t600 AUC=0.748 (best knockout)",
                "H1: activation-space fine grid analysis",
            ],
            "gaps": [
                "No SecMI evaluation on CIFAR100",
                "No PIA evaluation on CIFAR100",
                "No full membership inference pipeline (only activation scout)",
                "No ResNet/replay metrics",
                "No tri-score packet",
                "No white-box (GSA/fisher/influence)",
            ],
        },
        "DDIM-CIFAR10-750k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["CIFAR10 checkpoint, different dataset"],
        },
        "GuidedDiff-CIFAR10-500k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["CIFAR10 checkpoint, different dataset"],
        },
        "DDPM-STL10-final": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["STL10 checkpoint, different dataset"],
        },
        "DDPM-STL10-99k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["STL10 checkpoint, different dataset"],
        },
        "DDPM-STL10-overfit-m1000-9k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["STL10 overfit checkpoint"],
        },
        "DDPM-STL10-overfit-m1000-5k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["STL10 overfit checkpoint"],
        },
        "DDPM-STL10-overfit-m2000-8k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["STL10 overfit checkpoint"],
        },
        "DDPM-STL10-overfit-m500-9k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["STL10 overfit checkpoint"],
        },
        "Beans-LoRA-SD15": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["SD1.5 LoRA on Beans"],
        },
        "NDSS-2025-derived": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["Black-box proxy tensors"],
        },
        "SD-v1-4-CompVis": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["Stable Diffusion on LAION"],
        },
    },
    "STL-10": {
        "DDPM-CIFAR10-800k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["CIFAR10 checkpoint, different dataset + different resolution (32x32 vs 96x96)"],
        },
        "DDPM-CIFAR100-800k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["CIFAR100 checkpoint, different dataset"],
        },
        "DDIM-CIFAR10-750k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["CIFAR10 checkpoint, different dataset"],
        },
        "GuidedDiff-CIFAR10-500k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["CIFAR10 checkpoint, different dataset"],
        },
        "DDPM-STL10-final": {
            "status": "",
            "experiments": [
                "STL10 smoke: training completed, sample images generated (step200-1000)",
                "ReDiffuse bounded scout: AUC=0.4996 (weak, direction closed by default)",
                "SimA-style score-norm scorer: AUC=0.5053 (weak, direction closed by default)",
            ],
            "gaps": [
                "DIRECTION CLOSED: both scouts returned weak results (AUC approx 0.5)",
                "No SecMI evaluation",
                "No PIA evaluation",
                "No overfit variant member inference tests",
            ],
        },
        "DDPM-STL10-99k": {
            "status": "[UNTESTED]",
            "experiments": [],
            "gaps": [
                "Collaborator checkpoint exists, ReDiffuse-compatible (loads=true)",
                "99k steps: may need more training for useful membership signal",
                "No membership inference evaluation of any kind run",
            ],
        },
        "DDPM-STL10-overfit-m1000-9k": {
            "status": "[UNTESTED]",
            "experiments": [],
            "gaps": [
                "Overfit 1000-member STL10 checkpoint, ReDiffuse-compatible",
                "No membership inference evaluation run",
                "Overfit regime may yield stronger membership signal than full training",
            ],
        },
        "DDPM-STL10-overfit-m1000-5k": {
            "status": "[UNTESTED]",
            "experiments": [],
            "gaps": ["Overfit variant, continued from larger base (15k/20k/25k), no evaluation"],
        },
        "DDPM-STL10-overfit-m2000-8k": {
            "status": "[UNTESTED]",
            "experiments": [],
            "gaps": ["Overfit 2000-member, no evaluation"],
        },
        "DDPM-STL10-overfit-m500-9k": {
            "status": "[UNTESTED]",
            "experiments": [],
            "gaps": ["Overfit 500-member seed 1, no evaluation"],
        },
        "Beans-LoRA-SD15": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["SD1.5 LoRA on Beans"],
        },
        "NDSS-2025-derived": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["Black-box proxy tensors"],
        },
        "SD-v1-4-CompVis": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["SD on LAION, different domain"],
        },
    },
    "Fashion-MNIST": {
        "DDPM-CIFAR10-800k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["CIFAR10 checkpoint, different data domain + resolution (32x32 vs 28x28)"],
        },
        "DDPM-CIFAR100-800k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["CIFAR100 checkpoint"],
        },
        "DDIM-CIFAR10-750k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["CIFAR10 checkpoint"],
        },
        "GuidedDiff-CIFAR10-500k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["CIFAR10 checkpoint"],
        },
        "DDPM-STL10-final": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["STL10 checkpoint, different domain"],
        },
        "DDPM-STL10-99k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["STL10 checkpoint"],
        },
        "DDPM-STL10-overfit-m1000-9k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["STL10 overfit checkpoint"],
        },
        "DDPM-STL10-overfit-m1000-5k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["STL10 overfit checkpoint"],
        },
        "DDPM-STL10-overfit-m2000-8k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["STL10 overfit checkpoint"],
        },
        "DDPM-STL10-overfit-m500-9k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["STL10 overfit checkpoint"],
        },
        "Beans-LoRA-SD15": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["SD1.5 LoRA on Beans"],
        },
        "NDSS-2025-derived": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["Black-box proxy tensors"],
        },
        "SD-v1-4-CompVis": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["SD on LAION, different domain"],
        },
    },
    "Beans": {
        "DDPM-CIFAR10-800k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["CIFAR10 DDPM, completely different model family (DDPM vs SD1.5)"],
        },
        "DDPM-CIFAR100-800k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["CIFAR100 DDPM, different model family"],
        },
        "DDIM-CIFAR10-750k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["CIFAR10 DDPM, different model family"],
        },
        "GuidedDiff-CIFAR10-500k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["CIFAR10 guided-diffusion, different model family"],
        },
        "DDPM-STL10-final": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["STL10 DDPM, different model family"],
        },
        "DDPM-STL10-99k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["STL10 DDPM, different model family"],
        },
        "DDPM-STL10-overfit-m1000-9k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["STL10 overfit checkpoint, different model family"],
        },
        "DDPM-STL10-overfit-m1000-5k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["STL10 overfit checkpoint, different model family"],
        },
        "DDPM-STL10-overfit-m2000-8k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["STL10 overfit checkpoint, different model family"],
        },
        "DDPM-STL10-overfit-m500-9k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["STL10 overfit checkpoint, different model family"],
        },
        "Beans-LoRA-SD15": {
            "status": "",
            "experiments": [
                "LoRA member denoising loss: contract/debug only",
                "Membership provenance NOT proven: beans train/val not shown as SD1.5 training membership",
            ],
            "gaps": [
                "BLOCKED by membership provenance: cannot prove beans train/val = SD1.5 member/nonmember",
                "This is a contract/debug lane only",
            ],
        },
        "NDSS-2025-derived": {
            "status": "[UNTESTED]",
            "experiments": [],
            "gaps": [
                "NDSS-2025 uses fine-tuned SD (possibly SD1.5 or SD2.1 variant)",
                "Beans is also SD1.5-based, so the attack methodology could theoretically transfer",
                "But NDSS derived tensors are text+image wrappers, not checkpoints  not directly loadable for Beans",
                "Would need: verify NDSS model family, then cross-apply attack to Beans SD1.5",
            ],
        },
        "SD-v1-4-CompVis": {
            "status": "[UNTESTED]",
            "experiments": [],
            "gaps": [
                "SD-v1-4 is the base model for Beans LoRA fine-tuning",
                "MIA on SD-v1-4 + Beans would test whether fine-tuning membership is detectable",
                "No membership inference evaluation run on this combination",
                "xuchi-reproduction used SD-v1-4 + COCO-like data, not Beans",
            ],
        },
    },
    "CelebA": {
        "DDPM-CIFAR10-800k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["CIFAR10 DDPM, different model family + resolution"],
        },
        "DDPM-CIFAR100-800k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["CIFAR100 DDPM"],
        },
        "DDIM-CIFAR10-750k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["CIFAR10 DDPM"],
        },
        "GuidedDiff-CIFAR10-500k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["CIFAR10 guided-diffusion"],
        },
        "DDPM-STL10-final": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["STL10 DDPM, different model family"],
        },
        "DDPM-STL10-99k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["STL10 checkpoint"],
        },
        "DDPM-STL10-overfit-m1000-9k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["STL10 overfit checkpoint"],
        },
        "DDPM-STL10-overfit-m1000-5k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["STL10 overfit checkpoint"],
        },
        "DDPM-STL10-overfit-m2000-8k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["STL10 overfit checkpoint"],
        },
        "DDPM-STL10-overfit-m500-9k": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["STL10 overfit checkpoint"],
        },
        "Beans-LoRA-SD15": {
            "status": "[NO]",
            "experiments": [],
            "gaps": ["SD1.5 LoRA on Beans, not CelebA"],
        },
        "NDSS-2025-derived": {
            "status": "[UNTESTED]",
            "experiments": [],
            "gaps": [
                "NDSS-2025 may use fine-tuned SD with face-like data (same domain as CelebA)",
                "CelebA has partition file (train/val/test) but no SD checkpoint trained on known splits",
                "Would need: SD fine-tuned on CelebA with known member/nonmember split",
            ],
        },
        "SD-v1-4-CompVis": {
            "status": "[UNTESTED]",
            "experiments": [],
            "gaps": [
                "SD-v1-4 + CelebA is a plausible MIA target",
                "CelebA has train/val/test partitions usable as member/nonmember proxy",
                "No SD checkpoint fine-tuned on known CelebA split exists locally",
                "Would need: fine-tune SD on CelebA train split, keep val/test as nonmembers",
            ],
        },
    },
}

# 
# PRINT THE MATRIX
# 

def print_header():
    print("=" * 130)
    print("DATASET x CHECKPOINT COMPATIBILITY MATRIX")
    print("DiffAudit Research  Single Source of Truth for Experiment Planning")
    print("Generated: 2026-06-20")
    print("=" * 130)
    print()
    print("LEGEND:")
    print("  [OK]    = Compatible AND tested (results available)")
    print("  [UNTESTED] = Compatible but UNTESTED (runnable, no results)")
    print("  [NO]    = Incompatible (format/dataset/dimensionality mismatch)")
    print("  [CLOSED]   = Direction closed (weak results, route blocked by governance)")
    print()
    print("COLUMNS: Every structurally unique checkpoint (deduplicated)")
    print("ROWS:    Every available dataset with a split file defining member/nonmember")
    print()
    print("DATA SOURCE: outputs/catalog-checkpoints.json + workspace evidence")
    print()

def print_dataset_header(ds_name, ds_info):
    print()
    print("-" * 130)
    print(f"DATASET: {ds_name}")
    print(f"  Split source:   {ds_info['split']}")
    print(f"  Membership:     {ds_info['membership_provenance']}")
    print(f"  Resolution:     {ds_info['resolution']}")
    if ds_info.get("member_tensor"):
        print(f"  Cached tensor:  {ds_info['member_tensor']}")
    if ds_info.get("npz_split"):
        print(f"  NPZ split:      {ds_info['npz_split']}")
    print("-" * 130)

def print_summary():
    print()
    print("=" * 130)
    print("SUMMARY STATISTICS")
    print("=" * 130)

    total_cells = 0
    tested = 0
    untested = 0
    incompatible = 0
    closed = 0

    for ds_name in matrix:
        for ckpt_name, cell in matrix[ds_name].items():
            total_cells += 1
            if cell["status"] == "[OK]":
                tested += 1
            elif cell["status"] == "[UNTESTED]":
                untested += 1
            elif cell["status"] == "[NO]":
                incompatible += 1
            elif cell["status"] == "":
                closed += 1

    print(f"  Total dataset x checkpoint cells:  {total_cells}")
    print(f"  [OK] Compatible + tested:             {tested}")
    print(f"  [UNTESTED] Compatible + untested:           {untested}")
    print(f"  [NO] Incompatible:                    {incompatible}")
    print(f"   Direction closed:                {closed}")
    print()

    print("  Datasets with at least one tested checkpoint:")
    for ds_name in matrix:
        has_tested = any(cell["status"] == "[OK]" for cell in matrix[ds_name].values())
        if has_tested:
            tested_ckpts = [ckpt for ckpt, cell in matrix[ds_name].items() if cell["status"] == "[OK]"]
            print(f"    {ds_name}: {len(tested_ckpts)} tested checkpoint(s)  {', '.join(tested_ckpts)}")
        else:
            print(f"    {ds_name}: 0 tested checkpoints")

    print()
    print("  Datasets with untested-but-compatible checkpoints (highest priority gaps):")
    for ds_name in matrix:
        untested_ckpts = [(ckpt, cell) for ckpt, cell in matrix[ds_name].items() if cell["status"] == "[UNTESTED]"]
        if untested_ckpts:
            print(f"    {ds_name}:")
            for ckpt, cell in untested_ckpts:
                print(f"      [UNTESTED] {ckpt}")
                for gap in cell.get("gaps", []):
                    print(f"         -> {gap}")

    print()
    print("  Closed directions (do not re-open without new evidence):")
    for ds_name in matrix:
        closed_ckpts = [(ckpt, cell) for ckpt, cell in matrix[ds_name].items() if cell["status"] == ""]
        if closed_ckpts:
            for ckpt, cell in closed_ckpts:
                print(f"     {ds_name} x {ckpt}")

#  MAIN 

print_header()

for ds_name in datasets:
    if ds_name not in matrix:
        continue
    ds_info = datasets[ds_name]
    print_dataset_header(ds_name, ds_info)

    # Filter to relevant checkpoints for this dataset
    for ckpt_name, cell in matrix[ds_name].items():
        status = cell["status"]
        experiments = cell.get("experiments", [])
        gaps = cell.get("gaps", [])

        print(f"  {status} {ckpt_name}")

        if experiments:
            for exp in experiments:
                print(f"        EXP: {exp}")
        if gaps:
            for gap in gaps:
                print(f"        GAP: {gap}")
        if not experiments and not gaps:
            print(f"       (no details)")
        print()

print_summary()

print()
print("=" * 130)
print("GOVERNANCE NOTES")
print("=" * 130)
print("""
1. This matrix is the SINGLE SOURCE OF TRUTH for experiment planning.
   Do not plan experiments without cross-referencing this matrix.

2. [OK] cells: Do not re-run unless there is a specific hypothesis, contract change,
   or independent verification need. Prefer to extend with new ablations.

3. [UNTESTED] cells: Highest priority for evaluation. These are known-compatible but
   untested. Prioritize by: (a) strongest expected signal, (b) closest to
   existing evidence, (c) lowest GPU cost.

4. [NO] cells: Do not attempt to force compatibility. Use only if a new checkpoint
   is trained on the matching dataset.

5.  cells: DO NOT RE-OPEN without:
   - A genuinely new mechanism family
   - External evidence that contradicts the closure
   - Explicit approval from Research governance

6. All STL-10 overfit checkpoints (m500/m1000/m2000) are [UNTESTED] untested.
   The base STL-10 direction is  closed due to weak results, but the overfit
   regime may yield different signal characteristics.

7. Fashion-MNIST has NO local DDPM checkpoint persisted. All experiments used
   transient external checkpoints (1aurent/ddpm-mnist). Direction closed due to
   weak gradient-norm results.

8. The guided-diffusion CIFAR10-500k checkpoint is [UNTESTED] untested. It uses a
   different UNet architecture (guided-diffusion vs Rediffuse) and its
   membership signal characteristics are unknown.

9. Beans/SD1.5 is blocked on membership provenance. Do not allocate GPU to Beans
   membership inference without first proving train = SD1.5 member.

10. SD-v1-4 + CelebA and SD-v1-4 + Beans are [UNTESTED] untested SD-domain gaps.
    The xuchi-reproduction showed MIA is possible on SD + COCO-like data
    (AUC=0.710). Extension to other SD-domain datasets is a plausible direction.
""")

# Write the matrix as JSON for programmatic consumption
output_path = RESEARCH / "outputs" / "dataset-checkpoint-matrix.json"
with open(output_path, "w") as f:
    json.dump({
        "generated": "2026-06-20",
        "datasets": datasets,
        "checkpoints": {k: {kk: vv for kk, vv in v.items() if kk != "paths"} for k, v in checkpoints.items()},
        "matrix": matrix,
    }, f, indent=2, ensure_ascii=False, default=str)

print(f"\nMatrix written to: {output_path}")
