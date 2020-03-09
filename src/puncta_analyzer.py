import pandas as pd
import numpy as np
np.set_printoptions(threshold=np.inf)
import matplotlib.pyplot as plt
import tifffile

from math import sqrt
from skimage import feature
from skimage.color import rgb2gray

# A program to recognize puncta in an image 
# see https://scikit-image.org/docs/stable/auto_examples/features_detection/plot_blob.html#sphx-glr-auto-examples-features-detection-plot-blob-py
# for more detail


p = './data/'
fname = 'subtracted'
fname_ext = '.tif'

# we use tifffile instead of cv2.imread, skimage.imread because 
# tifffile handles loading 16-bit tiff files, while cv2, skimage assume
# they will be 8-bit tiff files
puncta_img = tifffile.imread(p + fname + fname_ext)

# a puncta is a row of tuples containing (x, y, sigma)
# where x, y is the pixel position in the image
# where sigma is proprotional to the punctums radius
puncta = feature.blob_log(puncta_img, max_sigma=5, overlap=0.9, threshold=.2)

# Compute radii of each punctum
# radius = sqrt(2) * sigma
puncta[:, 2] = puncta[:, 2] * sqrt(2)

# show the puncta image
fig, ax = plt.subplots(1)
ax.set_title('puncta')
ax.imshow(np.invert(puncta_img), cmap=plt.cm.binary, aspect='equal')

# show where each recognized punctum is on the image
for punctum in puncta:
    y, x, r = punctum
    punctum_marker = plt.Circle((x, y), r, color='blue', linewidth=1, fill=False)
    ax.add_patch(punctum_marker)

# plt.show()
plt.savefig(p + 'annotated-' + fname + '.png')

# compute puncta statistics
# save them as a csv
# for each puncta get x, y, radius (approximate), area (approximate), distances ?, pixel intensity(x, y)

puncta_stats_columns = ['x', 'y', 'radius (approximation)', 'area (approximation)', 'pixel intensity']
puncta_stats = []
for punctum in puncta:
    y, x, r = punctum
    punctum_pixel_intensity = puncta_img[int(y)][int(x)]
    area = ( r ** 2 ) * np.pi
    puncta_stats.append([x, y, r, area, punctum_pixel_intensity])

numpy_puncta_stats = np.array(puncta_stats)
pandas_punca_stats = pd.DataFrame(data=numpy_puncta_stats, columns=puncta_stats_columns)

pandas_punca_stats.to_csv(p + 'puncta-stats.csv')