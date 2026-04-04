"""Planning helpers for integrating the official SecMI attack flow."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from diffaudit.config import AuditConfig


@dataclass(frozen=True)
class SecmiPlan:
    entrypoint: str
    dataset: str
    data_root: str
    model_dir: str
    t_sec: int
    k: int
    batch_size: int


@dataclass(frozen=True)
class SecmiArtifacts:
    checkpoint_path: str
    flagfile_path: str


@dataclass(frozen=True)
class SecmiRunnerSpec:
    repo_root: str
    entrypoint_path: str
    python_module: str
    checkpoint_path: str
    flagfile_path: str
    dataset: str
    data_root: str
    t_sec: int
    k: int
    batch_size: int


REQUIRED_SECMI_WORKSPACE_FILES = (
    "mia_evals/secmia.py",
    "mia_evals/dataset_utils.py",
    "model.py",
    "diffusion.py",
)


def build_secmi_plan(config: AuditConfig) -> SecmiPlan:
    if config.attack.method != "secmi":
        raise ValueError(f"Unsupported attack method for SecMI plan: {config.attack.method}")

    dataset = config.assets.dataset_name
    data_root = config.assets.dataset_root
    model_dir = config.assets.model_dir
    params = config.attack.parameters

    if not dataset:
        raise ValueError("SecMI requires assets.dataset_name")
    if not data_root:
        raise ValueError("SecMI requires assets.dataset_root")
    if not model_dir:
        raise ValueError("SecMI requires assets.model_dir")
    if "t_sec" not in params:
        raise ValueError("SecMI requires attack.parameters.t_sec")
    if "k" not in params:
        raise ValueError("SecMI requires attack.parameters.k")

    return SecmiPlan(
        entrypoint="mia_evals/secmia.py",
        dataset=dataset,
        data_root=data_root,
        model_dir=model_dir,
        t_sec=int(params["t_sec"]),
        k=int(params["k"]),
        batch_size=int(params.get("batch_size", 32)),
    )


def resolve_secmi_artifacts(model_dir: str | Path) -> SecmiArtifacts:
    model_path = Path(model_dir)
    flagfile_path = model_path / "flagfile.txt"
    if not flagfile_path.exists():
        raise FileNotFoundError(f"Missing SecMI flagfile: {flagfile_path}")

    checkpoint_path = model_path / "checkpoint.pt"
    if not checkpoint_path.exists():
        candidates = sorted(model_path.glob("ckpt-step*.pt"))
        if not candidates:
            raise FileNotFoundError(f"No SecMI checkpoint found in {model_path}")
        checkpoint_path = candidates[-1]

    return SecmiArtifacts(
        checkpoint_path=str(checkpoint_path),
        flagfile_path=str(flagfile_path),
    )


def validate_secmi_workspace(workspace_dir: str | Path) -> dict[str, str]:
    workspace_path = Path(workspace_dir)
    missing = [
        relative_path
        for relative_path in REQUIRED_SECMI_WORKSPACE_FILES
        if not (workspace_path / relative_path).exists()
    ]
    if missing:
        raise FileNotFoundError(
            f"SecMI workspace is missing required files: {', '.join(missing)}"
        )

    return {
        "status": "ready",
        "workspace_dir": str(workspace_path),
        "entrypoint": str(workspace_path / "mia_evals" / "secmia.py"),
    }


def build_secmi_runner_spec(
    plan: SecmiPlan,
    artifacts: SecmiArtifacts,
    repo_root: str | Path,
) -> SecmiRunnerSpec:
    repo_path = Path(repo_root)
    entrypoint_path = repo_path / plan.entrypoint
    if not entrypoint_path.exists():
        raise FileNotFoundError(f"SecMI entrypoint not found: {entrypoint_path}")

    return SecmiRunnerSpec(
        repo_root=str(repo_path),
        entrypoint_path=str(entrypoint_path),
        python_module="mia_evals.secmia",
        checkpoint_path=artifacts.checkpoint_path,
        flagfile_path=artifacts.flagfile_path,
        dataset=plan.dataset,
        data_root=plan.data_root,
        t_sec=plan.t_sec,
        k=plan.k,
        batch_size=plan.batch_size,
    )
