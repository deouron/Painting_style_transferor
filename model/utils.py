import torch.nn as nn
import torch.nn.functional as F

from .constanst import device, content_layers_default, style_layers_default
from .model import Normalization, ContentLoss, StyleLoss


def get_style_model_and_losses(cnn,
                               normalization_mean,
                               normalization_std,
                               style_img,
                               content_img,
                               content_layers=content_layers_default,
                               style_layers=style_layers_default
                               ):
    normalization = Normalization(normalization_mean, normalization_std).to(device)

    content_losses = []
    style_losses = []

    model = nn.Sequential(normalization)

    step = 0
    for layer in cnn.children():
        if isinstance(layer, nn.Conv2d):
            step += 1
            name = f'conv_{step}'
        elif isinstance(layer, nn.ReLU):
            name = f'relu_{step}'
            layer = nn.ReLU(inplace=False)
        elif isinstance(layer, nn.MaxPool2d):
            name = f'pool_{step}'
        elif isinstance(layer, nn.BatchNorm2d):
            name = 'bn_{step}'
        else:
            raise RuntimeError(f'Unrecognized layer: {layer.__class__.__name__}')

        model.add_module(name, layer)

        if name in content_layers:
            target = model(content_img).detach()
            content_loss = ContentLoss(target)
            model.add_module(f"content_loss_{step}", content_loss)
            content_losses.append(content_loss)

        if name in style_layers:
            target_feature = model(style_img).detach()
            style_loss = StyleLoss(target_feature)
            model.add_module(f"style_loss_{step}", style_loss)
            style_losses.append(style_loss)

    for step in range(len(model) - 1, -1, -1):
        if isinstance(model[step], ContentLoss) or isinstance(model[step], StyleLoss):
            break

    model = model[:(step + 1)]

    return model, style_losses, content_losses
