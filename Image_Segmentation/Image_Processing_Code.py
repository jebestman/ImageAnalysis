import os
import pandas as pd
import imageio as io
from napari import layers
from napari.plugins.io import save_layers
import numpy as np
import napari  
from skimage import filters, morphology, measure, exposure, segmentation, restoration
import skimage.io as skio
from scipy import ndimage as ndi

path = str(input('What is the folder path?:'))
files = os.listdir(path)
data = skio.imread(files[0], plugin = 'tifffile')

z = int(input('Please input the z spacing for your image.'))

spacing = np.array([z, .184, .184])

# initializing the viewer
viewer = napari.Viewer()

def add_to_viewer(layer_name):
    viewer.add_image(
        layer_name,
        scale = spacing
    )

# adding the raw image to the viewer.
add_to_viewer(data)

view = str(input('Would you like to view the individual layers ater each operation? Note: It can potential slow down the program \n'
'if that is done. Otherwise, it will only show you the mask, the mask after morphological operations, labels, and points. Y or N')).upper()

# rescaled intensity
rescaled_intensity = exposure.rescale_intensity(data)

if view == 'Y':
    add_to_viewer(rescaled_intensity)  

# denoiser with the estimated sigma
sigma_est = restoration.estimate_sigma(rescaled_intensity, average_sigmas=True)
denoise = restoration.denoise_wavelet(rescaled_intensity, sigma = sigma_est, 
method = 'BayesShrink', mode='soft', rescale_sigma=True)

if view == 'Y':
    add_to_viewer(denoise)  

# median filter
median = filters.median(denoise)
if view == 'Y':
    add_to_viewer(median)

# sobel filter
edges_sobel = filters.sobel(median)
if view == 'Y':
    add_to_viewer(edges_sobel)

# adaptive histogram equalization
# multiplying the CLAHE to the edges sobel image. 
AHE = exposure.equalize_adapthist(data)
multiplied = edges_sobel * AHE
if view == 'Y':
    add_to_viewer(multiplied)

unsharp = filters.unsharp_mask(multiplied,radius = 2, amount = 1)
if view == 'Y':
    add_to_viewer(unsharp)

skeleton = skio.imread(files[1], plugin='tifffile')
for i in range(0,14):
    skeleton = morphology.dilation(skeleton)
    i+=1

median_skel = filters.median(skeleton)
ROI = unsharp*median_skel
if view == 'Y':
    add_to_viewer(ROI)

# multiotsu mask
multiotsu = filters.threshold_multiotsu(ROI, 2)
multiotsu_mask = ROI > multiotsu
add_to_viewer(multiotsu_mask)

# morphological operations
multiotsu_closing = morphology.binary_closing(multiotsu_mask)
multiotsu_opening = morphology.binary_opening(multiotsu_closing)
multiotsu_dilation = morphology.binary_dilation(multiotsu_opening)
multiotsu_CODE = morphology.binary_erosion(multiotsu_dilation)
add_to_viewer(multiotsu_CODE)

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

# saving images
save_image = str(input('Would you like to save any of the images? Y or N')).upper()
if save_image == 'Y':
    image_name = str(input('Please input the name of the layer in napari that you would like to export. This is case sensitive. \n'
    'If you would like to save all of them, type "All".'))
    if image_name == 'All':
        save_layers(path, viewer.layers)
        print('Images will be saved in the folder provided previously.')
    else:
        layers.save(path, image_name)
        print('The image will be saved in the folder provided previously.')


# exporting properties

export = str(input('Would you like to export a csv table of the properties? Y or N')).upper()
if export == 'Y':
    properties = ['label', 'area', 'bbox_area', 'bbox', 'mean_intensity', 'equivalent_diameter',
    'minor_axis_length', 'major_axis_length', 'centroid']
    props = measure.regionprops_table(label_image,intensity_image = data, properties = properties)
    df = pd.DataFrame(props).set_index('label')
    name = str(input('What would you like to name the file?'))+".xlsx"
    save_location = path + '\\' + name
    df.to_excel(save_location)
    print('The file has been saved in the same folder as the image.')
