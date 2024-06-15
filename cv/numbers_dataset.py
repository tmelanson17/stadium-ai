import os
import torch
import torch.nn.functional as F
from skimage.util import random_noise
from torch.utils.data import Dataset
from torchvision.io import read_image, ImageReadMode

class SaltPepperNoise(object):
    def __init__(self, amount_salt=0.05, amount_pepper=0.05):
        self.s = amount_salt
        self.p = amount_pepper

    def __call__(self, tensor):
        rand = torch.rand_like(tensor)
        salt_mask = rand < self.s
        pepper_mask = rand > (1-self.p)
        copy = tensor.clone()
        copy[salt_mask] = copy.max()
        copy[pepper_mask] = 0
        return copy

    def __repr__(self):
        return self.__class__.__name__

class RandomPadding(object):
    def __init__(self, pad_amount=10):
        self.total_pad = pad_amount

    def __call__(self, tensor):
        padding = torch.randint(self.total_pad, (2,))
        pad_left = padding[0]
        pad_top = padding[1]
        return F.pad(tensor, (pad_left, self.total_pad - pad_left, pad_top, self.total_pad - pad_top))


    def __repr__(self):
        return self.__class__.__name__

class HPNumbersDataset(Dataset):
    def __init__(self, img_dir, transform=None, target_transform=None):
        self.img_dir = img_dir
        self.transform = transform
        self.target_transform = target_transform
        self.image_files = os.listdir(img_dir)
        self.labels = list()
        for f in self.image_files:
            name, _ = os.path.splitext(f)
            self.labels.append(int(name))

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, idx):
        img_path = os.path.join(self.img_dir, self.image_files[idx])
        image = read_image(img_path, ImageReadMode.GRAY).to(torch.float32)
        image[image > 0] = torch.max(image)
        # Invert image
        image = torch.max(image) - image
        label = self.labels[idx]
        if self.transform:
            image = self.transform(image)
        if self.target_transform:
            label = self.target_transform(label)
        return image, label
