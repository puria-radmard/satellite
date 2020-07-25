# -*- coding: utf-8 -*-
"""losses.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/11-YB38T422RjYhjUSzSDRgFoBOgvgKKa
"""

import torch
import torch.nn as nn
import torch.nn.functional as f
import numpy as np


def cross_entropy(y, t, beta):
    # y is preds, t is labels as per Bishop
    # Normalise ratio
    mag = np.sqrt(beta ** 2 + 1)
    beta_ = beta / mag
    alpha_ = 1 / mag
    return beta_ * t * torch.log2(y) + alpha_ * (1 - t) * torch.log2(1 - y)


def perPixelCrossEntropy(preds, labels, HWs, class_weights=None):
    batch_size, n_classes, H, W = preds.shape
    if class_weights == None:
        class_weights = [1] * n_classes
    class_weights = torch.tensor(class_weights)
    class_weights = f.normalize(class_weights, dim=0)
    size = torch.prod(torch.tensor(labels.shape)).float()

    assert preds.shape == labels.shape
    class_losses = -(1 / size) * torch.sum(cross_entropy(preds, labels, beta), dim=(0, 2, 3))
    try:
        assert not any(torch.isnan(class_losses))
    except AssertionError:
        print("NaN found in cross entropy! preds {}, labels {}".format(preds, labels))

    try:
        return torch.dot(class_losses, class_weights.double())
    except RuntimeError:
        return torch.dot(class_losses, class_weights.float())


def jaccardIndex(preds, labels, class_weights=None):
    batch_size, n_classes, H, W = preds.shape
    if class_weights == None:
        class_weights = [1] * n_classes
    class_weights = torch.tensor(class_weights)
    class_weights = f.normalize(class_weights, dim=0)
    size = torch.prod(torch.tensor(labels.shape)).float()

    assert preds.shape == labels.shape
    class_indices = (1 / size) * torch.sum(
        preds * labels / (preds + labels - labels * preds + 1e-10), dim=(0, 2, 3)
    )
    try:
        assert not any(torch.isnan(class_indices))
    except AssertionError:
        print("NaN found in J index! preds {}, labels {}".format(preds, labels))

    try:
        return torch.dot(class_indices, class_weights.double())
    except RuntimeError:
        return torch.dot(class_indices, class_weights.float())


def ternausLossfunc(preds, labels, l=1, beta=1, HWs=None, JWs=None):
    # Derived from https://arxiv.org/abs/1801.05746
    H = perPixelCrossEntropy(preds, labels, beta, HWs)
    J = jaccardIndex(preds, labels, JWs)
    return H - l * torch.log(J + 1e-10)


class TernausLossFunc(nn.Module):
    def __init__(self, l=1, beta=1, HWs=None, JWs=None):
        """
    Beta is on positive side, so a higher beta stops false negatives more
    """
        super(TernausLossFunc, self).__init__()
        self.l = l
        self.beta = beta
        self.HWs = HWs
        self.JWs = JWs

    def forward(self, preds: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
        return ternausLossfunc(preds, labels, self.l, self.HWs, self.JWs)
