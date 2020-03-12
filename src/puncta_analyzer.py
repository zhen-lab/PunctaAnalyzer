import os
import time
from pathlib import Path
from math import sqrt, ceil

import click
import pandas as pd
import numpy as np
np.set_printoptions(threshold=np.inf)
import matplotlib.pyplot as plt
import tifffile
from skimage import feature, draw

def area_of_circle(radius):
    return radius ** 2 * np.pi

def puncta_density(num_puncta, img_width):
    return num_puncta / img_width

def punctum_intensity(puncta_img, punctum):
    y, x, r = punctum
    center = (int(y), int(x))
    radius = int(r)

    # get pixel coordinates at center inside circular area
    pixel_y_coordinates, pixel_x_coordinates = draw.circle(int(x), int(y), radius)

    # get pixel intensities at those coordinates
    punctum_region_intensity_values = puncta_img[pixel_x_coordinates, pixel_y_coordinates]

    # return average of these intensities
    return np.mean(punctum_region_intensity_values)

def find_all_tiff_files(root_path):
    return [ str(p.resolve()) for p in sorted(root_path.rglob('*.tif')) ]

def compute_puncta_stats(puncta_img, min_sigma, max_sigma, overlap, threshold):
    # a puncta is a row of tuples containing (x, y, sigma)
    # where x, y is the pixel position in the image
    # where sigma is proprotional to the punctums radius
    puncta = feature.blob_log(puncta_img, min_sigma=min_sigma, max_sigma=max_sigma, overlap=overlap, threshold=threshold)

    # Compute radii of each punctum
    # radius = sqrt(2) * sigma
    puncta[:, 2] = puncta[:, 2] * sqrt(2)

    puncta_stats = []
    for punctum in puncta:
        y, x, r = punctum
        centroid_pixel_intensity = puncta_img[int(y)][int(x)]
        area = area_of_circle(r)
        punctum_intesity_over_area = punctum_intensity(puncta_img, punctum)

        puncta_stats.append([x, y, r, area, centroid_pixel_intensity, punctum_intesity_over_area])

    return np.array(puncta_stats), len(puncta_stats)

def save_stats_to_file(stats, output_path, columns):
    if stats.size == 0:
        stats = None

    pd_stats = pd.DataFrame(data=stats, columns=columns)
    pd_stats.to_csv(output_path)


# A program to recognize puncta in an image
# see https://scikit-image.org/docs/stable/auto_examples/features_detection/plot_blob.html#sphx-glr-auto-examples-features-detection-plot-blob-py
# for more detail
@click.command()
@click.argument('input_path', nargs=1, type=click.Path(exists=True))
@click.argument('output_path', nargs=1, type=click.Path(exists=True, file_okay=False))
@click.option('-lo','--min-sigma', type=click.IntRange(1, 100), default=1, help='Lower values detect smaller puncta', show_default=True)
@click.option('-hi', '--max-sigma', type=click.IntRange(1, 100), default=10, help='Higher values detect larger puncta', show_default=True)
@click.option('-t', '--threshold', type=click.FloatRange(0.0, 1.0), default=.1, help='Higher values remove puncta with duller intensity', show_default=True)
@click.option('-ov', '--overlap', type=click.FloatRange(0.0, 1.0), default=0.7, help='If the fraction of overlap between two puncta is greater than this value, remove the smaller puncta', show_default=True)
@click.option('--save-annotated', is_flag=True, default=False, help='Show recognized puncta in image', show_default=True)
def puncta_analyzer(input_path, output_path, min_sigma, max_sigma, threshold, overlap, save_annotated):
    """analyze puncta tiff files"""

    p = Path(input_path)

    tiff_file_paths = []
    if p.is_dir():
        tiff_file_paths = find_all_tiff_files(p)
    else:
        tiff_file_paths.append(str(p.resolve()))

    puncta_stats_columns = [
        'x',
        'y',
        'radius (approximation)',
        'area (approximation)',
        'centroid pixel intensity',
        'mean pixel intensity'
    ]

    puncta_img_set_stats_columns = [
        'tiff file path',
        'tiff image width',
        'number of puncta',
        'puncta density'
    ]

    # This will hold aggregate image stats
    # e.g. puncta density for each image analyzed
    puncta_img_set_stats = []

    for tiff_file_path in tiff_file_paths:
        # we use tifffile instead of cv2.imread, skimage.imread because
        # tifffile handles loading 16-bit tiff files, while cv2, skimage assume
        # they will be 8-bit tiff files
        puncta_img = tifffile.imread(tiff_file_path)
        puncta_img_h, puncta_img_w = puncta_img.shape
        puncta_stats, num_puncta = compute_puncta_stats(puncta_img, min_sigma, max_sigma, overlap, threshold)
        base_tiff_name = os.path.basename(tiff_file_path)
        tiff_name_no_ext, _ = os.path.splitext(base_tiff_name)

        cur_img_stats_f_name = Path(output_path) / (tiff_name_no_ext + '-puncta-stats-' + time.strftime("%Y%m%d-%H%M%S") + '.csv')

        # save puncta specific stats for each image
        save_stats_to_file(puncta_stats, cur_img_stats_f_name.resolve(), puncta_stats_columns)

        puncta_img_set_stats.append([tiff_file_path, puncta_img_w, num_puncta, puncta_density(num_puncta, puncta_img_w)])

        if save_annotated:
            # show the puncta image
            fig, ax = plt.subplots(1)
            ax.set_title('puncta')
            ax.imshow(np.invert(puncta_img), cmap=plt.cm.binary)

            # show where each recognized punctum is on the image
            for punctum in puncta_stats:
                x, y, r, _, _, _ = punctum
                punctum_marker = plt.Circle((x, y), r, color='blue', linewidth=1, fill=False)
                ax.add_patch(punctum_marker)

            fig_save_path = Path(output_path) / ( tiff_name_no_ext + '-annotated-' + time.strftime("%Y%m%d-%H%M%S") + '.png' )
            plt.savefig(fig_save_path.resolve())

            # show the figure if there is only one file to be processed
            if len(tiff_file_paths) == 1:
                plt.show()

    img_set_stats_output_file_name = Path(output_path) / ('puncta-img-set-stats-' + time.strftime("%Y%m%d-%H%M%S") + '.csv')
    save_stats_to_file(np.array(puncta_img_set_stats), img_set_stats_output_file_name, puncta_img_set_stats_columns)

if __name__ == '__main__':
    puncta_analyzer()