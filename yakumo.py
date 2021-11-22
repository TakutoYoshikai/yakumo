from PIL import Image
import os
import argparse
import random

IV_SIZE = 128 # bit
SEPARATOR_SIZE = 128 # bit
END_SEPARATOR_SIZE = 128 # bit
FILE_SEPARATOR_SIZE = 128

METADATA_SIZE = SEPARATOR_SIZE + END_SEPARATOR_SIZE + FILE_SEPARATOR_SIZE

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
    return lsb

def get_all_lsbs_and_iv(images):
    lsbs = []
    for image in images:
        lsbs.extend(get_lsbs(image))
    iv = lsbs[0:128]
    lsbs = lsbs[128:]
    size = len(lsbs) - (len(lsbs) % 8)
    lsbs = lsbs[0:size]
    return (lsbs, iv)

def get_all_lsbs(images):
    lsbs = []
    for image in images:
        lsbs.extend(get_lsbs(image))
    size = len(lsbs) - (len(lsbs) % 8)
    lsbs = lsbs[0:size]
    return lsbs

def to_bytes(lsb):
    return bytes([sum([byte[b] << b for b in range(0, 8)]) for byte in zip(*(iter(lsb),) * 8)])

def get_metadata(lsbs):
    index = 0
    separator = lsbs[index:SEPARATOR_SIZE]
    index += SEPARATOR_SIZE
    end_separator = lsbs[index:END_SEPARATOR_SIZE]
    index += END_SEPARATOR_SIZE
    file_separator = lsbs[index:FILE_SEPARATOR_SIZE]
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
            end_index = _bytes.find(end_separator)
            splitted.append(_bytes[0:end_index + 1])
            break;
        splitted.append(_bytes[0:index + 1])
        _bytes = _bytes[index + 1:]
    return splitted

def get_filename_and_data(_bytes, file_separator):
    index = _bytes.find(file_separator)
    return (_bytes[0:index + 1].decode(), _bytes[index + 1:])


def export_file(filename, data):
    with open("./" + filename, "w") as f:
        f.write(data)


def export_files(dr):
    image_paths = get_image_path_list(dr)
    images = get_image_list(image_paths)
    lsbs = get_all_lsbs(images)
    metadata = get_metadata(lsbs)
    lsbs = metadata["usbs"]
    files = list(map(lambda f: get_filename_and_data(f, metadata["file_separator"]), split(lsbs, metadata["separator"], metadata["end_separator"])))
    for file in files:
        filename, data = file
        export_file(filename, data)

def create_lsb(data_dir):
    separator = os.urandom(SEPARATOR_SIZE / 8)
    end_separator = os.urandom(END_SEPARATOR_SIZE / 8)
    file_separator = os.urandom(FILE_SEPARATOR_SIZE / 8)
    lsbs = bytes()
    lsbs.extend(separator)
    lsbs.extend(end_separator)
    file_paths = list(filter(lambda f: os.path.isfile(f), os.listdir(data_dir)))
    file_data_list = []
    for path in file_paths:
        filename = os.path.basename(path)
        with open(path, "rb") as f:
            one_file = bytes()
            data = f.read()
            one_file.extend(filename)
            one_file.extend(file_separator)
            one_file.extend(data)
            one_file.extend(separator)
            lsbs.extend(one_file)
    lsbs.extend(end_separator)
    return lsbs


            




    
    



