# -*- coding: utf-8 -*-
"""train-unet.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1tzchg3Y2KhH976SCNo7J8y89ABg8tRcI
"""

# Commented out IPython magic to ensure Python compatibility.
import os
from glob import glob as glob
import json
import torch
import numpy as np
from skimage import io, transform
import matplotlib.pyplot as plt
from torch.utils.data import Dataset, DataLoader
import torch.optim as optim
import torch.nn as nn
import argparse

import sys

sys.path.append("/content/drive/My Drive/Satellite Imagery code")


from utils import (
    produceImage,
    trainEpoch,
    testModel,
    train_test_dataset,
    SatelliteDataset,
)
import unet
from config_utils import *
from perf_metrics import *

import wandb

import warnings

warnings.filterwarnings("ignore")

# %matplotlib inline

import sys
import time


def train_unet(
    config
):

    import pdb; pdb.set_trace()

    model = unet.UNet(dropout=config.dropout)

    if torch.cuda.is_available():
        torch.set_default_tensor_type("torch.cuda.FloatTensor")
        model.cuda()


    loss_func = loss_dict[config.loss_func](**config.loss_parameters)

    wandb.watch(model)

    print(len(glob(dataset + "/" + "images" + "/*")), "images found total")

    optimizer = optim.Adam(model.parameters(), lr=config.lr)
    train_dataset, test_dataset = train_test_dataset(
        config.dataset, test_size=config.test_size, train_size=config.train_size, random_state=config.random_state
    )
    train_dataloader = DataLoader(train_dataset, batch_size=config.batch_size)
    test_dataloader = DataLoader(
        test_dataset, batch_size=config.batch_size
    )  # Change to own batch size?

    train_num_steps = len(train_dataloader)
    eval_num_steps = len(test_dataloader)
    print(
        "Starting training for {} epochs of {} training steps and {} evaluation steps".format(
            num_epochs, train_num_steps, eval_num_steps
        )
    )

    # for epoch in range(recent_epoch + 1, recent_epoch + num_epochs + 1):
    for epoch in range(config.num_epochs):

        epoch_loss = trainEpoch(
            model, epoch, optimizer, train_dataloader, train_num_steps, loss_func
        )
        print(f"Training epoch {epoch} done")

        epoch_score = testModel(
            model, epoch, test_dataloader, eval_num_steps, test_metric[0]
        )
        print(f"Evaluating epoch {epoch} done")

        produceImage(model, epoch, config.dir_name, config.dataset)

        epoch_metrics = {
            f"epoch_loss": epoch_loss,
            f"epoch_score": epoch_score,
        }

        wandb.log(epoch_metrics)

        if (epoch + 1) % save_rate == 0:
            print(f"      Saving to saves/{config.dir_name}/epoch_{epoch}")
            torch.save(model.state_dict(), f"saves/{config.dir_name}/epoch_{epoch}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Give loss function, evaluation metric, and hyperparameters"
    )
    parser.add_argument("--loss_func", type=str)
    parser.add_argument("--loss_parameters", type=str)
    parser.add_argument("--test_metric", type=str)
    parser.add_argument("--dataset", type=str)
    parser.add_argument("--lr", type=float)
    parser.add_argument("--dir_name", type=str)
    parser.add_argument("--test_size", type=float)
    parser.add_argument("--train_size", type=float, default=None)
    parser.add_argument("--batch_size", type=int)
    parser.add_argument("--dropout", type=float)
    parser.add_argument("--save_rate", type=int)
    parser.add_argument("--random_state", type=int, default=1)
    parser.add_argument("--num_epochs", type=int, default=20)

    args = parser.parse_args()

    loss_parameters = args.loss_parameters
    with open(loss_parameters, "r") as loss_parameters_file:
        loss_parameters = json.load(loss_parameters_file)

    test_size = args.test_size
    train_size = args.train_size

    if train_size == None:
        train_size = 1 - args.test_size

    config = {
        "test_metric": args.test_metric,
        "loss_func": args.loss_func,
        "num_epochs": args.num_epochs,
        "save_rate": args.save_rate,
        "random_state": args.random_state,
        "dataset": args.dataset,
        "dir_name": args.dir_name,
        "test_size": test_size,
        "train_size": train_size,
        "lr": args.lr,
        "dropout": args.dropout,
        "batch_size": args.batch_size,
        "loss_parameters": loss_parameters,
    }

    wandb.init(project="unet", config=config)

    train_unet(wandb.config)
