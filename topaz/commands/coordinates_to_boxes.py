from __future__ import print_function,division

import sys
import os
import numpy as np
import pandas as pd
from PIL import Image

from topaz.utils.conversions import coordinates_to_boxes


name = 'coordinates_to_boxes'
help = 'convert coordinates table to .box format files per image'


def add_arguments(parser):
    parser.add_argument('paths', nargs='+',  help='path to input coordinates file')
    parser.add_argument('--destdir', required=True, help='directory to write per image files')
    parser.add_argument('--boxsize', required=True, type=int, help='size of particle boxes')

    parser.add_argument('--invert-y', action='store_true', help='invert (mirror) the y-axis particle coordinates. appears to be necessary for .tiff compatibility with EMAN2')
    parser.add_argument('--imagedir', help='directory of images. only required to invert the y-axis - necessary for particles picked on .tiff images in EMAN2')
    parser.add_argument('--image-ext', default='tiff', help='image format extension, * corresponds to matching the first image file with the same name as the box file (default: tiff)')

    return parser


def main(args):
    dfs = []
    for path in args.paths:
        coords = pd.read_csv(path, sep='\t')
        dfs.append(coords)
    coords = pd.concat(dfs, axis=0)

    coords = coords.drop_duplicates()

    if not os.path.exists(args.destdir):
        os.makedirs(args.destdir)

    invert_y = args.invert_y

    for image_name,group in coords.groupby('image_name'):
        path = args.destdir + '/' + image_name + '.box'

        shape = None
        if invert_y:
            impath = os.path.join(args.imagedir, image_name) + '.' + args.image_ext
            # use glob incase image_ext is '*'
            impath = glob.glob(impath)[0]
            im = load_image(impath)
            shape = (im.height,im.width)
        
        xy = group[['x_coord', 'y_coord']].values.astype(np.int32)

        boxes = coordinates_to_boxes(xy, args.boxsize, args.boxsize, shape=shape, invert_y=invert_y)
        boxes = pd.DataFrame(boxes)

        boxes.to_csv(path, sep='\t', header=False, index=False)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser('Script for converting coordinates for images in one file to multiple files')
    add_argument(parser)
    args = parser.parse_args()
    main(args)


