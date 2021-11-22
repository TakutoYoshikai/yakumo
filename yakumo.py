from PIL import Image
import os
import argparse
import random
import glob
import sys

IV_SIZE = 128 # bit
SEPARATOR_SIZE = 128 # bit
END_SEPARATOR_SIZE = 128 # bit
FILE_SEPARATOR_SIZE = 128 # bit

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
    for image_path in image_paths:
        images.append(Image.open(image_path).convert("RGB"))
    return images

def set_lsb(component, bit):
    return component & ~1 | int(bit)

def get_bit(c):
    return c & 1

def get_lsbs(image):
    lsb = []
    buf = []
    for y in range(image.size[1]):
        for x in range(image.size[0]):
            pixel = image.getpixel((x, y))
            if image.mode == "RGBA":
                pixel = pixel[:3]
            for color in pixel:
                lsb.append(get_bit(color))
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
    lsbs = lsbs[:size]
    return lsbs

def to_bytes(lsb):
    return bytes([sum([byte[b] << (7 - b) for b in range(0, 8)]) for byte in zip(*(iter(lsb),) * 8)])

def get_metadata(lsbs):
    index = 0
    separator = lsbs[index:SEPARATOR_SIZE]
    index += SEPARATOR_SIZE
    end_separator = lsbs[index:index+END_SEPARATOR_SIZE]
    index += END_SEPARATOR_SIZE
    file_separator = lsbs[index:index+FILE_SEPARATOR_SIZE]
    new_lsbs = lsbs[METADATA_SIZE:]
    return {
        "separator": to_bytes(separator),
        "end_separator": to_bytes(end_separator),
        "file_separator": to_bytes(file_separator),
        "lsbs": new_lsbs,
    }
    

def split(lsbs, separator, end_separator):
    _bytes = to_bytes(lsbs)
    splitted = []
    while True:
        index = _bytes.find(separator)
        if index == -1:
            #end_index = _bytes.find(end_separator)
            #splitted.append(_bytes[0:end_index + 1])
            break;
        splitted.append(_bytes[0:index])
        _bytes = _bytes[int(SEPARATOR_SIZE / 8) + index:]
    return splitted

def get_filename_and_data(_bytes, file_separator):
    index = _bytes.find(file_separator)
    return (_bytes[0:index].decode(), _bytes[index + int(FILE_SEPARATOR_SIZE / 8):])


def export_file(filename, data):
    with open("./" + filename, "wb") as f:
        f.write(data)


def export_files(dr):
    image_paths = get_image_path_list(dr)
    images = get_image_list(image_paths)
    lsbs = get_all_lsbs(images)
    metadata = get_metadata(lsbs)
    lsbs = metadata["lsbs"]
    files = list(map(lambda f: get_filename_and_data(f, metadata["file_separator"]), split(lsbs, metadata["separator"], metadata["end_separator"])))
    for file in files:
        filename, data = file
        export_file(filename, data)

def create_lsb(data_dir):
    separator = os.urandom(int(SEPARATOR_SIZE / 8))
    end_separator = os.urandom(int(END_SEPARATOR_SIZE / 8))
    file_separator = os.urandom(int(FILE_SEPARATOR_SIZE / 8))
    lsbs = bytearray()
    lsbs.extend(separator)
    lsbs.extend(end_separator)
    lsbs.extend(file_separator)
    file_paths = glob.glob(data_dir + "/*")
    for path in file_paths:
        filename = os.path.basename(path)
        with open(path, "rb") as f:
            one_file = bytearray()
            data = f.read()
            one_file.extend(filename.encode())
            one_file.extend(file_separator)
            one_file.extend(data)
            one_file.extend(separator)
            lsbs.extend(one_file)
    lsbs.extend(end_separator)
    return lsbs

def message_to_binary(message):
    if type(message) == str:
        return ''.join([ format(ord(i), "08b") for i in message])
    elif type(message) == bytes:
        return [ format(i, "08b") for i in message ]
    elif type(message) == bytearray:
        return [ format(i, "08b") for i in bytes(message) ]
    elif type(message) == int:
        return format(message, "08b")

def embed(image_dir, data_dir):
    image_paths = get_image_path_list(image_dir)
    images = get_image_list(image_paths)
    data = create_lsb(data_dir)
    binary = list(map(lambda x: int(x), "".join(message_to_binary(data))))
    index = 0
    for path, image in zip(image_paths, images):
        width, height = image.size
        for row in range(height):
            for col in range(width):
                if index < len(binary):
                    pixel = image.getpixel((col, row))
                    r = pixel[0]
                    g = pixel[1]
                    b = pixel[2]
                    r = set_lsb(r, binary[index])
                    if index + 1 < len(binary):
                        g = set_lsb(g, binary[index + 1])
                    if index + 2 < len(binary):
                        b = set_lsb(b, binary[index + 2])
                    if image.mode == "RGBA":
                        image.putpixel((col, row), (r, g, b, pixel[3]))
                    else:
                        image.putpixel((col, row), (r, g, b))
                    index += 3
                else:
                    image.save(path)
                    image.close()
                    return
        image.save(path)


            

if sys.argv[1] == "hide":
    embed(sys.argv[2], sys.argv[3])
elif sys.argv[1] == "reveal":
    export_files(sys.argv[2])



    
    


