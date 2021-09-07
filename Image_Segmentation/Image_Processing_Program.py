# Image Segmentation code for Bestman Lab

# Import Lines

## image processing and segmentation modules

import napari
import skimage
import skimage.io as skio
from scipy import ndimage as ndi 

## graphs and analysis modules

import pandas as pd 
import numpy as np 
import matplotlib
import matplotlib.pyplot as plt 
import plotly
import plotly.express as px
import plotly.graph_objects as go


class ImageProcessing:

    def __init__(self, filelocation):
        self.original_image = filelocation

    def image_read(self):
        # only reads in tiff files. Provide the file location for easier access

        image = skio.imread(self.original_image, plugin='tifffile')
        return image
    
    def histograms(self):
        # creates the histogram of the image

        fig, ax = plt.subplots(figsize=(8,4))
        
        ax.hist(self.image_read().flatten(), log=True)

        _ = ax.set_title('Min value: %i \n'
        'Max Value: %i \n'
        'Image shape: %i \n'
        % (self.image_read().min(),
        self.image_read().max(),
        self.image_read().shape))
 

    def spacing(self,x,y,z):
        # spacing for the viewer

        spacing = np.array([x,y,z])
        return spacing


    def Adaptive_Histo_Equal(self,image=None):
        # adaptive histogram equalization
        
        if image is None:
            data_AHE = skimage.exposure.equalize_adapthist(self.image_read())
        else:
            data_AHE = skimage.exposure.equalize_adapthist(image)
            
        return data_AHE


    def rescaled_intensity(self, image = None):
        # rescaled intensity of the image
        
        if image is None:
            intensity_rescaled = skimage.exposure.rescale_intensity(self.image_read())
        else:
            intensity_rescaled = skimage.exposure.rescale_intensity(image)
            
        return intensity_rescaled

    def create_viewer(self, start_image):
        # initialize the napari viewer

        viewer = napari.view_image(
            start_image,
            contrast_limits = [0,1],
            scale = self.spacing,
            ndisplay = 3,
)


    
