from Image_Processing import Image_Processing
import skimage.io as skio
import os
from skimage import measure
import napari 
import numpy as np
import pandas as pd 


path = str(input('What is the folder path?: '))
files = os.listdir(path)
data = skio.imread(path+ '\\' + files[0], plugin = 'tifffile')
z = float(input('Please input the z spacing for your image. '))
spacing = np.array([z, .184, .184])
skeleton = skio.imread(path + '\\' + files[1], plugin='tifffile')

# initializing the viewer
viewer = napari.Viewer()

image_analysis = Image_Processing(data, skeleton, spacing, viewer)


ROI, labels = image_analysis.image_analysis()
    
# exporting properties    
properties = ['label', 'area', 'bbox_area', 'bbox', 'mean_intensity', 'equivalent_diameter',
    'minor_axis_length', 'major_axis_length', 'centroid']
props = measure.regionprops_table(labels,intensity_image = ROI, properties = properties)
df = pd.DataFrame(props).set_index('label')
name = str(input('What would you like to name the file?: '))+".xlsx"
save_location = path + '\\' + name
df.to_excel(save_location)
print('The file has been saved in the same folder as the image.')
