# Image Segmentation code for Bestman Lab

# Import Lines

## image processing and segmentation modules

import napari
from napari.qt.threading import thread_worker
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
        self.file = filelocation
        self.image = None


    def image_read(self):
        # only reads in tiff files. Provide the file location for easier access

        self.image = skio.imread(self.file, plugin='tifffile')
        return self.image

    
    def histograms(self):
        # creates the histogram of the image

        fig, ax = plt.subplots(figsize=(8,4))
        
        ax.hist(self.image.flatten(), log=True)

        _ = ax.set_title('Min value: %i \n'
        'Max Value: %i \n'
        'Image shape: %i \n'
        % (self.image.min(),
        self.image.max(),
        self.image.shape))


    def Adaptive_Histo_Equal(self,image=None):
        # adaptive histogram equalization
        
        if image is None:
            data_AHE = skimage.exposure.equalize_adapthist(self.image)
            print('Using default image.')
        else:
            data_AHE = skimage.exposure.equalize_adapthist(image)
            
        return data_AHE


    def rescaled_intensity(self, image = None):
        # rescaled intensity of the image
        
        if image is None:
            intensity_rescaled = skimage.exposure.rescale_intensity(self.image)
            print('Using default image.')
        else:
            intensity_rescaled = skimage.exposure.rescale_intensity(image)
            
        return intensity_rescaled




    
