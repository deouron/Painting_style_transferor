from uuid import uuid4

import torch
import torch.optim as optim
import torch.nn.functional as F
import torchvision.models as models
from torchvision.utils import save_image
import PIL

from loguru import logger

from .preprocessing import preprocessing
from .utils import *


def run_style_transfer(cnn,
                       normalization_mean,
                       normalization_std,
                       content_img,
                       style_img,
                       input_img,
                       num_steps,
                       style_weight=1000000,
                       content_weight=1
                       ):
    logger.info('Building the style transfer model..')
    model, style_losses, content_losses = get_style_model_and_losses(cnn,
                                                                     normalization_mean, normalization_std, style_img,
                                                                     content_img)

    input_img.requires_grad_(True)
    model.requires_grad_(False)

    optimizer = optim.LBFGS([input_img])

    logger.info('Optimizing..')
    run = [0]
    while run[0] <= num_steps:

        def closure():
            with torch.no_grad():
                input_img.clamp_(0, 1)

            optimizer.zero_grad()
            model(input_img)
            style_score = 0
            content_score = 0

            for sl in style_losses:
                style_score += sl.loss
            for cl in content_losses:
                content_score += cl.loss

            style_score *= style_weight
            content_score *= content_weight

            loss = style_score + content_score
            loss.backward()

            run[0] += 1
            if run[0] % 5 == 0:
                logger.info("run {}:".format(run))
                logger.info('Style Loss : {:4f} Content Loss: {:4f}'.format(
                    style_score.item(), content_score.item()))

            return style_score + content_score

        optimizer.step(closure)

    with torch.no_grad():
        input_img.clamp_(0, 1)

    return input_img


def main(source_file: str,
         style_file: str,
         size: list,
         epochs: int = 10,
         style_weight: int = 1000000,
         content_weight: int = 1
         ) -> str:
    content_img, style_img = preprocessing(source_file=source_file, style_file=style_file, size=size,
                                           size_reduction=1)
    input_img = content_img.clone()

    cnn = models.vgg19(weights='DEFAULT').features.to(device).eval()

    output = run_style_transfer(cnn, cnn_normalization_mean, cnn_normalization_std,
                                content_img, style_img, input_img, num_steps=epochs, style_weight=style_weight,
                                content_weight=content_weight)

    generate_file_name = uuid4().hex
    logger.info(f'{generate_file_name}.jpg')
    save_image(output, f"Photos/modified_photos/{generate_file_name}.jpg")

    return f"{generate_file_name}.jpg"


if __name__ == '__main__':
    photo = main('AgACAgIAAxkBAAIBBmPNNYdCpJ8CZ5H9zdWmhlCTBD--AALWwzEbeSdpSqzRM6NN_s9YAQADAgADeQADLQQ',
                 'AgACAgIAAxkBAAIBA2PNNYKzFCsFlXGf6z7uUpEqJlwfAALVwzEbeSdpStsOizzbkCxhAQADAgADeAADLQQ')
