import torch as th
from typing import List, Sequence, Tuple
import os


class DiffusionTrajectoryFeaturesDataset(th.utils.data.Dataset):

    def __init__(self,
                 data_path: str,
                 start: int = 0,
                 end: int = -1,
                 step: int = 1,
                 loss_feat: bool = True,
                 grad_x_feat: bool = True,
                 grad_theta_feat: bool = True,
                 ma: bool = False,
                 mia: bool = False) -> None:
        """
        Args:
            data_path (str): Either a directory containing the pt files or a single pt file.
                The pt files contain tensors of shape (n_samples, n_features) where n_features = 3 * n_timesteps.
                The features are organized as:

                ```
                [l(0), l(1), ..., l(n_timesteps - 1),
                 gx(0), gx(1), ..., gx(n_timesteps - 1),
                 gtheta(0), gtheta(1), ..., gtheta(n_timesteps - 1)]
                ```

                where `l`, `gx`, and `gtheta` are the loss and gradient features.

            start (int): Index of the first time step to consider.
            end (int): Index of the last time step to consider.
            step (int): Number of time steps to hop.
            loss_feat (bool): Whether to include the loss features.
            grad_x_feat (bool): Whether to include the gradients with respect to the image features.
            grad_theta_feat (bool): Whether to include the gradients with respect to the model parameters features.
            ma (bool): Whether to load the data for model attribution (drops member data, don't use with `mia`).
            mia (bool): Whether to load the data for membership inference attack (drops belonging data, don't use with `ma`).

        Example directory structure:

        ```
        data_path
        ├── belonging.pt
        ├── external.pt
        ├── member.pt
        ```
        """  # noqa: E501

        self._len = 0
        self._loss_feat = loss_feat
        self._grad_x_feat = grad_x_feat
        self._grad_theta_feat = grad_theta_feat
        self._start = start
        self._end = end
        self._step = step

        self._CLS_NAMES = ['_' + cls for cls in class_list(ma, mia)]

        if os.path.isfile(data_path):
            # HACK: _external is used for the single file
            self._external = th.load(data_path)
            self._len += len(self._external)
            self._CLS_NAMES = ['_external']

        else:
            for cls in self._CLS_NAMES:
                setattr(self, cls, th.load(os.path.join(data_path, f'{cls[1:]}.pt')))
                self._len += len(getattr(self, cls))

        self._slice_start_end_step()
        self._select_features()

    def __len__(self) -> int:
        return self._len

    def __getitem__(self, idx) -> Tuple[th.Tensor, th.Tensor]:
        """
        Args:
            idx (int): Index of the sample to return.

        Returns:
            Tuple[Tensor, Tensor]: A tuple containing the features and the class number.
                If loading from a single file, the class defaults to 0.
        """

        for cls_idx, cls in enumerate(self._CLS_NAMES):
            if idx < len(getattr(self, cls)):
                return getattr(self, cls)[idx], th.tensor(cls_idx)
            idx -= len(getattr(self, cls))

    def _slice_start_end_step(self) -> None:
        """
        Slice timesteps. Call this before _select_features.
        """

        start, end, step = self._start, self._end, self._step

        for split in self._CLS_NAMES:
            data = getattr(self, split)
            T = data.shape[1] // 3
            if end == -1:
                end = data.shape[1] // 3

            setattr(self, split, th.cat((data[:, start:end:step],
                                         data[:, T + start:T + end:step],
                                         data[:, 2 * T + start:2 * T + end:step]), dim=1))

    def _select_features(self) -> None:

        for split in self._CLS_NAMES:
            data = getattr(self, split)
            selected = []
            third_features = data.shape[1] // 3
            if self._loss_feat:
                selected.append(data[:, :third_features])
            if self._grad_x_feat:
                selected.append(data[:, third_features: 2 * third_features])
            if self._grad_theta_feat:
                selected.append(data[:, 2 * third_features:])
            setattr(self, split, th.cat(selected, dim=1))

    @property
    def n_features(self) -> int:
        return self._external.shape[1]


def class_list(ma: bool, mia: bool) -> List[str]:
    if ma:
        return ["external", "belonging"]
    elif mia:
        return ["member", "external"]
    return ["member", "external", "belonging"]


class LinearClassifier(th.nn.Module):

    def __init__(self,
                 in_features: int = 3000,
                 out_features: int = 3) -> None:
        super().__init__()
        self.out_features = 1 if out_features == 2 else out_features
        self.fc = th.nn.Linear(in_features=in_features, out_features=self.out_features)
        self.register_buffer("mean", th.zeros(1, in_features))
        self.register_buffer("std", th.ones(1, in_features))

    def forward(self, x: th.Tensor) -> th.Tensor:
        x = (x - self.mean) / self.std
        x = self.fc(x)
        if self.out_features > 1:
            return x
        return th.cat((x, th.zeros_like(x)), dim=1)


def calculate_var_mean(dataset: DiffusionTrajectoryFeaturesDataset, model: LinearClassifier) -> None:
    """
    Calculate the mean and variance of the features and store them in the model.
    """

    features = th.cat([getattr(dataset, cls) for cls in dataset._CLS_NAMES], dim=0)

    var, mean = th.var_mean(features, dim=0, keepdim=True)
    model.mean.copy_(mean)
    model.std.copy_(var.sqrt())


def print_normalized_confusion_matrix(matrix: Sequence, labels: Sequence) -> None:
    num_classes = len(labels)
    cell_width = max(
        max(len(str(matrix[i][j].item())) for i in range(num_classes) for j in range(num_classes)),
        max(len(label) for label in labels),
        len("True / Predicted")
    ) + 2

    header = "True / Predicted".ljust(cell_width) + " | " + " | ".join([f"{label.capitalize():^{cell_width}}"
                                                                        for label in labels]) + " |"
    print(header)
    print("-" * len(header))

    for i in range(num_classes):
        row = f"{labels[i].capitalize():<{cell_width}} | " + " | ".join([f"{matrix[i][j].item():^{cell_width}.1f}"
                                                                         for j in range(num_classes)]) + " |"
        print(row)
        print("-" * len(row))
