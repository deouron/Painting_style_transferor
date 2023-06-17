import torch
import torchvision.transforms as transforms
from PIL import Image

from .utils import *


def image_loader(image_name: str, size: list, size_reduction: int) -> torch.Tensor:
    image = Image.open(image_name)
    loader = transforms.Compose([
        transforms.Resize((size[1] // size_reduction, size[0] // size_reduction)),
        transforms.ToTensor()
    ])

    image = loader(image).unsqueeze(0)
    return image.to(device, torch.float)


def preprocessing(source_file: str, style_file: str, size: list, size_reduction: int = 1):
    style_img = image_loader(f'Photos/style_photos/{style_file}.jpg', size, size_reduction)
    source_img = image_loader(f'Photos/style_photos/{source_file}.jpg', size, size_reduction)

    return source_img, style_img


if __name__ == "__main__":
    print(type(image_loader('../style_photos/style_3.jpg')))
