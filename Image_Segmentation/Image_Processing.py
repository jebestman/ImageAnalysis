import os
import pandas as pd
import imageio as io
import numpy as np
import napari  
from skimage import filters, morphology, measure, exposure, segmentation, restoration, feature, util
import skimage.io as skio
from scipy import ndimage as ndi

class Image_Processing():

    def __init__(self, image, skeleton, spacing, viewer):
        self.image = image
        self.skeleton = skeleton
        self.spacing = spacing
        self.viewer = viewer
        self.median_skel = None

    def add_to_viewer(self, image_name, layer_name):
        self.viewer.add_image(
            image_name,
            name = layer_name,
            scale = self.spacing
        )
    

    def image_analysis(self):
        def __skeleton():
            skel = self.skeleton
            for i in range(0,10):
                skel = morphology.dilation(skel)
                i+=1
                
            self.median_skel = filters.median(skel)
        
        __skeleton()
        
        p, y, x = np.where(self.skeleton)
        p1 = min(p)
        p2 = max(p)
        row1 = min(x)
        row2 = max(x)
        col1 = min(y)
        col2 = max(y)
        ROI = self.image[p1:p2, col1:col2, row1:row2]
        skele = self.median_skel[p1:p2, col1:col2, row1:row2]
        self.add_to_viewer(ROI, 'ROI')
        self.add_to_viewer(skele, 'Skeleton')
        #cropped_skeleton = viewer.layers['Skeleton']
        
        
        selem = morphology.cube(3)

        # median filter
        median = filters.median(ROI, selem = selem)
        median = util.img_as_float(median)

        print('Median filter operation is complete.')
        self.add_to_viewer(median, 'median')
        print('The image has been added to the viewer')

        background = filters.gaussian(median, 7.0)
        print('Background operation computed')
        self.add_to_viewer(background, 'background')

        subtract = median - background
        self.add_to_viewer(subtract, 'subtract')

        AHE = exposure.equalize_adapthist(subtract)
        multiplied = AHE * subtract
        self.add_to_viewer(multiplied, 'multiplied')

        thresh = filters.threshold_multiotsu(image = multiplied, classes = 2)
        otsu = multiplied >= thresh
        print('Otsu mask operation is complete.')

        self.add_to_viewer(otsu, 'otsu_mask')
        print('The image has been added to the viewer')


        # morphological operations
        otsu_dilate = morphology.binary_dilation(otsu)
        otsu_closing = morphology.binary_closing(otsu_dilate)
        print('Morphological operations are complete.')
        final_mask = np.where(skele, otsu_closing, 0)

        self.add_to_viewer(final_mask, 'final_mask')
        print('The image has been added to the viewer')

        # adding labels and points to the image
        cleared = segmentation.clear_border(final_mask)
        label_image = measure.label(cleared)
        boundaries = segmentation.find_boundaries(label_image)
        self.viewer.add_labels(
            boundaries,
            scale=self.spacing,
        )
        print('The labels have been added to the viewer')
        
        return ROI, label_image
