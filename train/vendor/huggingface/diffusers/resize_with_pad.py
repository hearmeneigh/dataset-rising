# based on:
# https://github.com/pytorch/vision/issues/6236#issuecomment-1175971587

import random
import torchvision.transforms.functional as F


# Resizes with aspect ratio, then pads to target size with random positioning
class ResizeWithPad:
    def __init__(self, interpolation: F.InterpolationMode, target_width: int, target_height: int):
        self.target_width = target_width
        self.target_height = target_height
        self.interpolation = interpolation

    def __call__(self, image):
        w_1, h_1 = image.size
        ratio_f = self.target_width / self.target_height
        ratio_1 = w_1 / h_1

        # check if the original and final aspect ratios are the same within a margin
        if round(ratio_1, 2) != round(ratio_f, 2):

            # padding to preserve aspect ratio
            hp = int(w_1/ratio_f - h_1)
            wp = int(ratio_f * h_1 - w_1)

            if hp > 0 and wp < 0:
                hp = hp // 2

                # left, top, right, bottom
                lr_pad = random.randint(0, hp)
                tb_pad = random.randint(0, hp)
                padding = [lr_pad, tb_pad, hp - lr_pad, hp - tb_pad]

                image = F.pad(image, padding, 0, "constant")
                return F.resize(image, [self.target_height, self.target_width], interpolation=self.interpolation, antialias=True)

            elif hp < 0 and wp > 0:
                wp = wp // 2

                # left, top, right, bottom
                lr_pad = random.randint(0, wp)
                tb_pad = random.randint(0, wp)
                padding = [lr_pad, tb_pad, wp - lr_pad, wp - tb_pad]

                image = F.pad(image, padding, 0, "constant")
                return F.resize(image, [self.target_height, self.target_width], interpolation=self.interpolation, antialias=True)

        else:
            return F.resize(image, [self.target_height, self.target_width], interpolation=self.interpolation, antialias=True)

