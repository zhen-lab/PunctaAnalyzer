import click
import pandas as pd
import numpy as np
np.set_printoptions(threshold=np.inf)
import matplotlib.pyplot as plt
import tifffile

from math import sqrt, ceil
from skimage import feature, draw
from skimage.color import rgb2gray

def area_of_circle(radius):
    return radius ** 2 * np.pi

def puncta_density(puncta, img_width):
    return len(puncta) / img_width

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

# A program to recognize puncta in an image 
# see https://scikit-image.org/docs/stable/auto_examples/features_detection/plot_blob.html#sphx-glr-auto-examples-features-detection-plot-blob-py
# for more detail
@click.command()
@click.argument('tiff_file_path', nargs=-1, type=click.Path(exists=True, dir_okay=False))
@click.argument('output_path', nargs=1, type=click.Path(exists=True, file_okay=False))
@click.option('-lo','--min_sigma', type=click.IntRange(1, 100), default=1, help='Lower values detect smaller puncta', show_default=True)
@click.option('-hi', '--max_sigma', type=click.IntRange(1, 100), default=5, help='Higher values detect larger puncta', show_default=True)
@click.option('-t', '--threshold', type=click.FloatRange(0.0, 1.0), default=.2, help='Higher values remove puncta with duller intensity', show_default=True)
@click.option('-ov', '--overlap', type=click.FloatRange(0.0, 1.0), default=0.9, help='If the fraction of overlap between two puncta is greater than this value, remove the smaller puncta', show_default=True)
@click.option('--show_annotated', is_flag=True, default=False, help='Show recognized puncta in image', show_default=True)
def puncta_analyzer(tiff_file_path, output_path, min_sigma, max_sigma, threshold, overlap, show_annotated):
    """analyze puncta tiff files"""

    # we use tifffile instead of cv2.imread, skimage.imread because 
    # tifffile handles loading 16-bit tiff files, while cv2, skimage assume
    # they will be 8-bit tiff files
    puncta_img = tifffile.imread(tiff_file_path)

    # a puncta is a row of tuples containing (x, y, sigma)
    # where x, y is the pixel position in the image
    # where sigma is proprotional to the punctums radius
    puncta = feature.blob_log(puncta_img, min_sigma=min_sigma, max_sigma=max_sigma, overlap=overlap, threshold=threshold)

    # Compute radii of each punctum
    # radius = sqrt(2) * sigma
    puncta[:, 2] = puncta[:, 2] * sqrt(2)

    # compute puncta statistics
    # save them as a csv
    puncta_stats_columns = ['x', 'y', 'radius (approximation)', 'area (approximation)', 'centroid pixel intensity', 'average pixel intensity over punctum area']
    puncta_stats = []
    for punctum in puncta:
        y, x, r = punctum
        centroid_pixel_intensity = puncta_img[int(y)][int(x)]
        area = area_of_circle(r)
        punctum_intesity_over_area = punctum_intensity(puncta_img, punctum)
        
        puncta_stats.append([x, y, r, area, centroid_pixel_intensity, punctum_intesity_over_area])

    numpy_puncta_stats = np.array(puncta_stats)
    pandas_punca_stats = pd.DataFrame(data=numpy_puncta_stats, columns=puncta_stats_columns)

    pandas_punca_stats.to_csv(output_path + 'puncta-stats.csv')

    if show_annotated:
        # show the puncta image
        fig, ax = plt.subplots(1)
        ax.set_title('puncta')
        ax.imshow(np.invert(puncta_img), cmap=plt.cm.binary, aspect='auto')

        # show where each recognized punctum is on the image
        for punctum in puncta:
            y, x, r = punctum
            punctum_marker = plt.Circle((x, y), r, color='blue', linewidth=1, fill=False)
            ax.add_patch(punctum_marker)

        plt.show()

if __name__ == '__main__':
    puncta_analyzer()