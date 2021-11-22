from PIL import Image
import os
import argparse

IV_SIZE = 128 # bit
SEPARATOR_SIZE = 128 # bit
END_SEPARATOR_SIZE = 128 # bit
FILE_SEPARATOR = 128

METADATA_SIZE = SEPARATOR_SIZE + END_SEPARATOR_SIZE

def get_image_path_list(dr):
    imagenames = list(filter(lambda x: x.endswith(".png"), os.listdir(dr)))
    imagepaths = []
    for imagename in imagenames:
        imagepath = dr + "/" + imagename
        imagepaths.append(imagepath)
    return imagepaths

def get_image_list(image_paths):
    images = []
    for imagepath in imagepaths:
        images.append(Image.open(imagepath).convert("RGB"))
    return images

def set_lsb(component, bit):
    return component & ~1 | int(bit)

def get_bit(c):
    return c & 1

def get_lsbs(image):
    lsb = []
    for y in range(image.size[1]):
        for x in range(image.size[0]):
            r, g, b = image.getpixel((x, y))
            r = get_bit(r)
            g = get_bit(g)
            b = get_bit(b)
            lsb.append(r)
            lsb.append(g)
            lsb.append(b)

def get_all_lsbs_and_iv(images):
    lsbs = []
    for image in images:
        lsbs.extend(get_lsbs(image))
    iv = lsbs[0:128]
    lsbs = lsbs[128:]
    size = len(lsbs) - (len(lsbs) % 8)
    lsbs = lsbs[0:size]
    return (lsbs, iv)

def to_bytes(lsb):
    return bytes([sum([byte[b] << b for b in range(0, 8)]) for byte in zip(*(iter(lsb),) * 8)])

def get_metadata(lsbs):
    index = 0
    separator = lsbs[index:SEPARATOR_SIZE]
    index += SEPARATOR_SIZE
    end_separator = lsbs[index:END_SEPARATOR_SIZE]
    new_lsbs = lsbs[METADATA_SIZE:]
    return {
        "separator": to_bytes(separator),
        "end_separator": to_bytes(end_separator),
        "lsbs": new_lsbs,
    }
    

def split(lsbs, separator, end_separator):
    _bytes = to_bytes(lsbs)
    splitted = []
    while True:
        index = _bytes.find(separator)
        if index == -1:
            break;
        splitted.append([0:index + 1])
        _bytes = _bytes[index + 1:]
    return splitted

def get_filename_and_data(_bytes):
    index = _bytes.find(FILE_SEPARATOR)
    return (_bytes[0:index + 1].decode(), _bytes[index + 1:])


