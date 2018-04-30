import numpy as np
import argparse
import cv2
import sys

parser = argparse.ArgumentParser(
    description='Steganography program that puts data into pictures, give it a try!')
parser.add_argument('image', help='input image file')
parser.add_argument(
    'file', help='input file for compression output for extraction')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-x', action='store_true',
                   help='data extraction from image')
group.add_argument('-c', action='store_true', help='compress data into image')
args = parser.parse_args()

imgmask = int('00000011', 2)
imgdelmask = int('11111100', 2)
mask = int('11000000', 2)
pos = 0


def advance(mask, pos):
    mask >>= 2
    if mask == 0:
        mask = int('11000000', 2)
        pos += 1
    return mask, pos


def getbits(mask, i):
    while mask != 3:
        mask >>= 2
        i >>= 2
    return i

def getshift(mask):
    shifts = 0
    while mask > imgmask:
        mask >>= 2
        shifts += 2
    return shifts

def itb(i):
    return int(i).to_bytes(1, byteorder='big')


def bti(b):
    return int.from_bytes(b, byteorder='big')


img = cv2.imread(args.image)
w, h, c = img.shape
if args.c:
    # compression mode
    with open(args.file, 'rb') as f:
        data = f.read()
    # check if compression is possible
    imsize = w * h * c
    if imsize * 2 >= len(data)*8 + 32:
        # if 2 bits per image byte is bigger than
        # 8 bits * data bytes number + 32 bits (length encoding in bytes)
        # OK, compressing
        size = len(data)
        size = size.to_bytes(4, byteorder='big')
        data = size + data
        size = len(data)
        for i in range(w):
            if pos >= size:
                break
            for j in range(h):
                if pos >= size:
                    break
                for k in range(c):
                    # get current bits
                    b = data[pos] & mask
                    s = getshift(mask)
                    b = b >> s
                    # put them in image
                    img[i][j][k] = (img[i][j][k] & imgdelmask) | b
                    mask, pos = advance(mask, pos)
                    if pos >= size:
                        break
        imgname, imgext = '.'.join(args.image.split(
            '.')[:-1]), args.image.split('.')[-1]
        cv2.imwrite(imgname + '_COMPRESSED' + '.' + 'png', img )
    else:
        print('The image file is too small to compress this file..')
else:
    # extraction mode
    data = [0]
    # get file size
    # initially set file size to 5 to read the 4 bytes of size
    size = 4
    donesize = False
    for i in range(w):
        if pos >= size:
            break
        for j in range(h):
            if pos >= size:
                break
            for k in range(c):
                # get current bits
                b = img[i][j][k] & imgmask
                s = getshift(mask)
                b = b << s
                data[pos] = data[pos] | b
                # check if growing pos
                mask, pos = advance(mask, pos)
                if pos == len(data):
                    data.append(0)
                if pos == 4 and not donesize:
                    size = bti(data[:-1]) + 4
                    donesize = True
    with open(args.file, 'wb') as f:
       f.write(b''.join(map(itb, data[5:size])))
