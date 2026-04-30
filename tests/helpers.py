from __future__ import annotations

import json
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from typing import Any, Callable

import numpy as np
from PIL import Image


def capture_cli_json(main: Callable[[list[str]], int], argv: list[str]) -> tuple[int, dict[str, Any]]:
    stdout = StringIO()
    with redirect_stdout(stdout):
        exit_code = main(argv)
    return exit_code, json.loads(stdout.getvalue())


def make_fake_cifar10(pixel_values: tuple[int, ...] | list[int]):
    class FakeCIFAR10:
        def __init__(self, root, train, transform=None, download=False):
            del root, train, download
            self.transform = transform
            self.images = [
                np.full((32, 32, 3), fill_value=value, dtype=np.uint8)
                for value in pixel_values
            ]

        def __len__(self) -> int:
            return len(self.images)

        def __getitem__(self, index: int):
            image = Image.fromarray(self.images[index])
            tensor = self.transform(image) if self.transform is not None else image
            return tensor, index

    return FakeCIFAR10


def create_fake_secmi_repo(root: Path) -> Path:
    repo_root = root / "third_party" / "secmi"
    (repo_root / "mia_evals").mkdir(parents=True)
    (repo_root / "__init__.py").write_text('"""secmi"""', encoding="utf-8")
    (repo_root / "model.py").write_text("# model", encoding="utf-8")
    (repo_root / "diffusion.py").write_text("# diffusion", encoding="utf-8")
    (repo_root / "mia_evals" / "__init__.py").write_text('"""mia"""', encoding="utf-8")
    (repo_root / "mia_evals" / "dataset_utils.py").write_text("# util", encoding="utf-8")
    (repo_root / "mia_evals" / "secmia.py").write_text(
        "def get_FLAGS(*args, **kwargs):\n    return None\n"
        "def secmi_attack(*args, **kwargs):\n    return None\n",
        encoding="utf-8",
    )
    return repo_root


def write_secmi_flagfile(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "--T=100",
                "--ch=32",
                "--ch_mult=1",
                "--ch_mult=2",
                "--num_res_blocks=1",
                "--attn=1",
                "--dropout=0.1",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path

