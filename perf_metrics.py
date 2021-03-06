# -*- coding: utf-8 -*-
"""perf_metrics.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/16wWWrD_-T-Tq59VWQXFwAkjHZjOx9CFE
"""

import torch
import torch.nn as nn


def dice_coef(preds, labels):
    smooth = 1.0
    preds = preds.cpu().detach()
    labels = labels.cpu().detach()

    preds_flat = preds.view(-1)
    labels_flat = labels.view(-1)
    intersection = (preds_flat * labels_flat).sum()

    return (2.0 * intersection + smooth) / (
        preds_flat.sum() + labels_flat.sum() + smooth
    )
