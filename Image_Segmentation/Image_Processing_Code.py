import os
import pandas as pd
import imageio as io
import numpy as np
import napari  
from skimage import filters, morphology, measure, exposure, segmentation, restoration
from skimage.exposure.exposure import rescale_intensity
import skimage.io as skio
import scipy.stats as st
from scipy import ndimage as ndi

import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import plotly
import plotly.express as px
import plotly.graph_objects as go

path = str(input('What is the folder path?:'))
files = os.listdir(path)
mito_Channel = skio.imread(files[0], plugin = 'tifffile')

z = int(input('Please input the z spacing for your image.'))

spacing = np.array([z, .184, .184])

# initializing the viewer
viewer = napari.Viewer()

viewer.add_image(
    mito_Channel,
    scale = spacing
)

view = str(input('Would you like to view the individual layers? After each operation? Note: It can potential slow down the program \n'
'if that is done. Otherwise, it will only show you the mask, the mask after morphological operations, labels, and points. Y or N')).upper()

# rescaled intensity
rescaled_intensity = exposure.rescale_intensity(mito_Channel)

if view == 'Y':
    viewer.add_image(
    rescaled_intensity,
    scale = spacing
    )   

# denoiser with the estimated sigma
sigma_est = restoration.estimate_sigma(rescaled_intensity, average_sigmas=True)
denoise = restoration.denoise_wavelet(rescaled_intensity, sigma = sigma_est, 
method = 'BayesShrink', mode='soft', rescale_sigma=True)

if view == 'Y':
    viewer.add_image(
    denoise,
    scale = spacing
)

# median filter
median = filters.median(denoise)
if view == 'Y':
    viewer.add_image(
    median,
    scale = spacing
)

# sobel filter
edges_sobel = filters.sobel(median)
if view == 'Y':
    viewer.add_image(
    median,
    scale = spacing
)

# adaptive histogram equalization
# multiplying the CLAHE to the edges sobel image. 
data_adap = exposure.equalize_adapthist(mito_Channel)
multiplied = edges_sobel * data_adap
if view == 'Y':
    viewer.add_image(
        multiplied,
        scale=spacing,
    )

unsharp = filters.unsharp_mask(multiplied,radius = 2, amount = 1)
if view == 'Y':
    viewer.add_image(
        unsharp,
        scale=spacing,
    )

skeleton = skio.imread(files[2], plugin='tifffile')
for i in range(0,10):
    skeleton = morphology.dilation(skeleton)
    i+=1

median_skel = filters.median(skeleton)
ROI = unsharp*median_skel
if view == 'Y':
    viewer.add_image(
        ROI,
        scale=spacing,
    )

# multiotsu mask
multiotsu = filters.threshold_multiotsu(ROI, 2)
multiotsu_mask = ROI > multiotsu
viewer.add_image(
        multiotsu_mask,
        scale=spacing,
)

# morphological operations
multiotsu_closing = morphology.binary_closing(multiotsu_mask)
multiotsu_opening = morphology.binary_opening(multiotsu_closing)
multiotsu_dilation = morphology.binary_dilation(multiotsu_opening)
multiotsu_CODE = morphology.binary_erosion(multiotsu_dilation)
viewer.add_image(
        multiotsu_CODE,
        scale=spacing,
    )

# adding labels and points to the image
cleared = segmentation.clear_border(multiotsu_CODE)
label_image = measure.label(cleared)
boundaries = segmentation.find_boundaries(label_image)
viewer.add_labels(
        boundaries,
        scale=spacing,
    )

transformed = ndi.distance_trasnform_edt(multiotsu_CODE, sampling=spacing)
smooth_distance = filters.gaussian(transformed)
maxima = morphology.local_maxima(smooth_distance)
labeled_maxima = measure.label(maxima, connectivity = maxima.ndim)
viewer.add_points(
        np.transpose(np.nonzero(labeled_maxima)),
        name = 'points',
        scale = spacing,
        size = 4,
        n_dimensional = True,
)


# exporting properties

export = str(input('Would you like to export a csv table of the properties? Y or N')).upper()
if export == 'Y':
    properties = ['label', 'area', 'bbox_area', 'bbox', 'mean_intensity', 'equivalent_diameter',
    'minor_axis_length', 'major_axis_length', 'centroid']
    props = measure.regionprops_table(label_image,intensity_image = mito_Channel, properties = properties)
    df = pd.DataFrame(props).set_index('label')
    name = str(input('What would you like to name the file?'))+".xlsx"
    df.to_excel(path+ '\\' + name)
    print('The file has been saved in the same folder as the image.')
