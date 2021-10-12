from collections import OrderedDict

from PIL import Image


class EnglishTranslations:
    title = 'Image compression'
    open_btn_lbl = 'Open'
    interpolation_lbl = 'Interpolation method'
    images = 'Images'
    all_files = 'All files'
    download_lbl = 'Download'
    compressions = OrderedDict([
        (Image.NEAREST, 'Nearest'),
        (Image.BOX, 'Box'),
        (Image.BILINEAR, 'Bilinear'),
        (Image.HAMMING, 'Hamming'),
        (Image.BICUBIC, 'Bicubic'),
        (Image.LANCZOS, 'Lanczos'),
    ])
