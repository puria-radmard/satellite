# -*- coding: utf-8 -*-
"""utils

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1PhkXTMRdLg4DZw01tFEbWI6ziVn4Hp_2
"""

# Commented out IPython magic to ensure Python compatibility.
import os
from glob import glob as glob
import torch
import numpy as np
from skimage import io, transform
import matplotlib.pyplot as plt
from torch.utils.data import Dataset, IterableDataset, DataLoader
import random
import sys
import cv2
import time
import wandb
import subprocess
import cv2

# Ignore warnings
import warnings

warnings.filterwarnings("ignore")

# %matplotlib inline


class SatelliteDataset(Dataset):
    def __init__(
        self,
        root_dir,
        name_list,
        images_dir="images",
        labels_dir="labels",
        type_="train",
        channels=3,
        transform=None,
        label_axis=-1,
    ):
        self.images_dir = images_dir
        self.labels_dir = labels_dir
        self.name_list = name_list
        self.root_dir = root_dir
        self.channels = channels
        self.transform = transform
        self.label_axis = label_axis
        self.type_ = type_

        try:
            assert self.type_ in ["train", "test", "media"]
        except AssertionError:
            raise ValueError(
                f"Type of dataset needs to be train/test/media, not '{self.type_}'"
            )

    def __len__(self):
        return len(self.name_list)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        img_name = os.path.join(self.root_dir, self.images_dir, self.name_list[idx])
        image = io.imread(img_name)
        image = image[:, :, :-1] / 127.5 - 1

        label = None
        if self.type_ != "media":
            label_name = os.path.join(
                self.root_dir, self.labels_dir, self.name_list[idx]
            )
            label = io.imread(label_name)
            label = label[:, :, :1] / np.amax(label)
            label = torch.tensor(label).permute(2, 0, 1)

            if self.transform:
                sample = self.transform(sample)

        sample = (
            {"image": image, "label": label} if self.type_ != "media" else image
        )

        return sample


def trainEpoch(model, epoch, optimizer, dataloader, num_steps, loss_fn):

    model.train()

    epoch_loss_tot = 0
    start_time = time.time()

    for step, batch in enumerate(dataloader):

        images = batch["image"]
        labels = batch["label"]
        preds = model.forward(images)
        labels = torch.tensor(labels).type_as(preds)
        loss = loss_fn(preds, labels)
        loss.backward()
        model.float()
        optimizer.step()

        epoch_loss_tot += loss.mean()
        epoch_loss = epoch_loss_tot / ((step + 1))
        steps_left = num_steps - step
        time_passed = time.time() - start_time

        ETA = (time_passed / (step + 1)) * (steps_left)
        ETA = "{} m  {} s".format(np.floor(ETA / 60), int(ETA % 60))

        string = "Epoch: {}   Step: {}   Batch Loss: {:.4f}   Epoch Loss: {:.4f}   Epoch ETA: {}".format(
            epoch, step, loss, epoch_loss.mean(), ETA
        )

        sys.stdout.write("\r" + string)
        time.sleep(0.5)

        wandb.log({"iteration_loss": loss.mean()})

        if step == num_steps:
            break

    return epoch_loss


def testModel(model, epoch, dataloader, num_steps, test_metric):

    model.eval()

    epoch_score_tot = 0
    start_time = time.time()

    for step, batch in enumerate(dataloader):

        images = batch["image"]
        labels = batch["label"]
        preds = model.forward(images)
        labels = torch.tensor(labels).type_as(preds)
        score = test_metric(preds, labels)

        epoch_score_tot += score.mean()
        epoch_score = epoch_score_tot / ((step + 1))
        steps_left = num_steps - step
        time_passed = time.time() - start_time

        ETA = (time_passed / (step + 1)) * (steps_left)
        ETA = "{} m  {} s".format(np.floor(ETA / 60), int(ETA % 60))

        string = "Evaluating epoch: {}   Step: {}   Batch score: {:.4f}   Epoch score: {:.4f}   Epoch ETA: {}".format(
            epoch, step, score, epoch_score.mean(), ETA
        )

        sys.stdout.write("\r" + string)
        time.sleep(0.5)

        del preds
        del labels
        del images

        if step == num_steps:
            break

    print(f"Epoch: {epoch}, test metric: {epoch_score}")
    return epoch_score


from sklearn.model_selection import train_test_split


def train_test_dataset(
    data_dir,
    test_size=0.3,
    train_size=None,
    images_dir="images",
    labels_dir="labels",
    transform=None,
    random_state=None,
):

    if train_size == None:
        train_size = 1.0 - test_size
    assert test_size + train_size <= 1.0

    name_list = [x.split("/")[-1] for x in glob(data_dir + "/" + images_dir + "/*")]

    if random_state:
        train_list, test_list = train_test_split(
            name_list,
            test_size=test_size,
            train_size=train_size,
            random_state=random_state,
        )
    else:
        train_list, test_list = train_test_split(
            name_list, test_size=test_size, train_size=train_size
        )

    print(f"{len(train_list)} training images, {len(test_list)} testing images")

    train_dataset = SatelliteDataset(
        data_dir, train_list, type_="train", channels=3, transform=transform
    )
    test_dataset = SatelliteDataset(
        data_dir, test_list, type_="test", channels=3, transform=None
    )

    return train_dataset, test_dataset


def produceImage(model, epoch, media_dir_name, data_dir, video=False, figsize=30):

    model.eval()

    fig, axarr = plt.subplots(2, 10)
    fig.suptitle(epoch, fontsize=12)
    fig.set_figheight(figsize)
    fig.set_figwidth(figsize * 5)

    name_list = [x.split("/")[-1] for x in glob(f"{data_dir}/mediaset/images/*.png")]
    dataset = SatelliteDataset(
        root_dir=f"{data_dir}/mediaset", name_list=name_list, type_="media"
    )
    dataloader = iter(DataLoader(dataset, batch_size=10))
    batch = next(dataloader)
    preds = model(batch)
    preds = preds.cpu().permute(0, 2, 3, 1).detach().numpy()
    batch = batch.cpu()

    for j in range(10):
        axarr[0][j].imshow(batch[j] + 1)
        axarr[1][j].imshow(preds[j, :, :, 0])
    plt.show()
    fig.savefig(f"media/{media_dir_name}/epoch_{epoch}.png")

    wandb.log(
        {"examples_images": wandb.Image(f"media/{media_dir_name}/epoch_{epoch}.png")}
    )


def create_video(media_path):

    video_name = "{}/video.avi".format(media_path)
    images = sorted([img for img in os.listdir(media) if img.endswith(".png")])
    frame = cv2.imread(os.path.join(save_path, images[0]))
    height, width, layers = frame.shape

    video = cv2.VideoWriter(video_name, 0, 1, (width, height))

    for image in images:
        video.write(cv2.imread(os.path.join(save_path, image)))

    cv2.destroyAllWindows()
    video.release()


def loadRecentModel(save_path):
    """
  Deprecated as of 12/7/2020, but may be used again
  
  Usage
  
  recent_epoch, recent_model = utils.loadRecentModel(save_path)
  if recent_model != None:
    model.load_state_dict(torch.load(recent_model))
  """
    saves = sorted(glob(f"{save_path}/*"))
    if len(saves) == 0:
        print(f"No saves found in directory {save_path}")
        return 0, None
    else:
        recent_model = max(saves, key=os.path.getctime)
        print(f"Loading save from {recent_model}")
        try:
            recent_epoch = recent_model.split(".")[-2][-1]
        except:
            recent_epoch = recent_model[-1]
        try:
            int(recent_epoch)
        except:
            raise Exception(
                f"Invalid file name for recent model {recent_model}, should be of format epoch_#"
            )
        return int(recent_epoch), recent_model


def generateBoundaryMap(mask_dir, save_dir):
    mask = cv2.imread(mask_dir)

    gray_image = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    # Apply cv2.threshold() to get a binary image
    ret, thresh = cv2.threshold(gray_image, 50, 255, cv2.THRESH_BINARY)

    # Find contours:
    contours, hierarchy = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
    )

    # Draw contours:
    boundary = np.zeros(mask.shape)
    cv2.drawContours(boundary, contours, -1, (0, 255, 0), 2)

    cv2.imwrite(save_dir, boundary)


def produceBoundaryMaps():

    subprocess.call(["mkdir", "boundaries"])

    mask_dirs = glob("labels/*.png")

    save_dirs = [f"boundaries/{n}" for n in [a.split("/")[-1] for a in mask_dirs]]

    for i in range(len(mask_dirs)):

        generateBoundaryMap(mask_dirs[i], save_dirs[i])
