from logging import raiseExceptions
import os
import napari 
import numpy as np
import pandas as pd 
import imageio as io
from skimage import filters, morphology, measure, exposure, segmentation, restoration, feature, util
import skimage.io as skio
from scipy import ndimage as ndi

class Image_Processing():
    '''
    A class that will perform image processing operations.

    ...

    Attributes
    ----------
    image: ndarray
        an image to be processed
    skeleton: ndarray
        the skeleton of the image to be processed
    spacing: float
        the z spacing of the image
    viewer: napari.viewer
        the viewer to be used to view the image layers in 3D

    Methods
    -------
    skeleton_dilation(dilation=10)
        Dilates the skeleton of the image as many times as you indicate. 
        Crops the image to only the region of interest
    get_cropped()
        returns the cropped image
    median_filter(image, cube_width)
        Performs the median filter operation from skimage on the image passed. 
        Uses the cube width provided.
    background_subtract(image, gauss_sigma)
        Subtracts the background from the passed in image. Uses the gaussian 
        filter from skimage on the image passed in.
    sobel(image)
        Performs the sobel transformation on the passed in image using the sobel 
        filter from skimage
    ahe_contrast(image)
        Performs the adaptive histogram equalization on the passed in image using 
        the equalize_adapthist from skimage. Multiplies the image to the image 
        passed in to improve the contrast
    rescaled_intensity(image, vmin, vmax)
        Performs the rescale intensity operation on the passed in image using the 
        operation from skimage
    multiotsu_mask(image, classes)
        Performs the multiotsu mask operation using threshold_multiots from skimage 
        using the number of classes specified
    otsu_mask(image)
        Performs the otsu mask operation using threshold_otsu from skimage
    li_mask(image)
        Performs the li mask operation using threshold_li from skimage
    yen_mask(image)
        Performs the yen mask operation using threshold_yen from skimage
    default_morphology(image)
        Uses a default morphology operation consisting of closing and dilation 
        morphological operations.
    closing(image)
        Performs the closing operation on the provided mask 
    opening(image)
        Performs the opening operation on the provided mask 
    dilation(image)
        Performs the dilation operation on the provided mask 
    erosion(image)
        Performs the erosion operation on the provided mask 
    labels(image)
        Generates labels based on the mask created
    region_props(labels, intensity_image, properties)
        Generates the region properties from the labels depending on the properties 
        selected
    '''

    def __init__(self, image, skeleton, spacing, viewer):
        '''
        Parameters
        ----------
        image : ndarray
            The image to use for analysis
        skeleton : ndarray
            The binary image used to identify the area of interest of the image
        spacing : float
            The z spacing of the images being passed
        viewer : napari viewer
            The viewer to use for visualization of the images
        '''

        self.image = image
        self.skeleton = skeleton
        self.spacing = spacing
        self.viewer = viewer
        self.ROI = None
        self.median_skel = None
        self.final_contrast = None
        self.altered_image = self.image
        self.mask = None
        self.mask_morph = self.mask  

    def skeleton_dilation(self, dilation=10):
        ''' Dilates the skeleton provide.
        
        If the argument `dilation` isn't passed in, the default
        dilation value is used. Crops the image to be analyzed 
        to keep the image size small.

        Parameters
        ----------
        dilation : int, optional
            The amount of dilation applied to the skeleton
            (default is 10)
        
        Returns
        -------
        ROI
            An array for the cropped image with the dimensions of the skeleton         
        cropped_skeleton
            An array for the cropped skeleton with the size of the skeleton
        '''
        try:
            skel = self.skeleton
            for i in range(0,dilation):
                skel = morphology.dilation(skel)
                i+=1
                
            self.median_skel = filters.median(skel)
            p, x, y = np.where(self.median_skel)
            p1 = min(p)
            p2 = max(p)
            row1 = min(x)
            row2 = max(x)
            col1 = min(y)
            col2 = max(y)
            self.ROI = self.image[p1:p2, row1:row2, col1:col2]
            self.cropped_skel = self.median_skel[p1:p2, row1:row2, col1:col2]
            return self.ROI, self.cropped_skel
        except TypeError as e:
            print(f'This is not a valid type. Expected ndarray, but got {e}')

        
    def get_cropped(self):
        ''' Returns the cropped image used in the analysis. '''
        try:
            return self.ROI
        except TypeError as e:
            print(f'This is not a valid type. Expected ndarray, but got {e}')


# -------------------- Processing Operations

    def median_filter(self,image = None, cube_width = 3):
        '''Performs the median filter operation from skimage 
        on the image passed.
        
        If the argument `cube_width` isn't provided, the default 
        value of 3 is passed.
        
        Parameters 
        ----------
        image : ndarray
            The image to apply the operation to
        cube_width : int, optional
            The width of the cube used as the footprint for the 
            filter (default is 3)

        Returns
        -------
        median
            The image after the median filter has been applied
        '''
        try:
            footprint = morphology.cube(cube_width)
            self.median = filters.median(image, selem = footprint)
            self.median = util.img_as_float(self.median)
            return self.median
        except TypeError as e:
            print(f'This is not a valid type. Expected ndarray, but got {e}')


    def background_subtract(self,image = None, gauss_sigma = 7):
        '''Subtracts the background from the image provided
        
        If the argument `gauss_sigma` isn't provided, the default 
        value of 7 is passed.
        
        Parameters 
        ----------
        image : ndarray
            The image to apply the operation to
        gauss_sigma : int, optional
            The sigma used for the gaussian operation (default is 7)

        Returns
        -------
        subtract
            The image with the same shape as the input image after the 
            subtraction has been applied
        '''
        try:
            background = filters.gaussian(image, gauss_sigma)
            self.subtract = image - background
            return self.subtract
        except TypeError as e:
            print(f'This is not a valid type. Expected ndarray, but got {e}')


    def sobel(self, image = None, mask = None):
        '''Performs the sobel transformation on a given image
        
        If the argument `mask` isn't provided, the mask will
        not be used.
        
        Parameters 
        ----------
        image : ndarray
            The image to apply the operation to
        mask : ndarray, optional
            mask to isolate the sobel filter to (default is None)

        Returns
        -------
        sobel
            The image of same shape as the input after the sobel filter 
            has been applied
        '''
        try:
            sobel = filters.sobel(image = image , mask = mask)
            return sobel
        except TypeError as e:
            print(f'This is not a valid type. Expected ndarray, but got {e}')


# -------------------- Contrast Options


    def ahe_contrast(self, image = None):
        '''Performs the adaptive histogram equalization operation
        and multiplies the provided image and the AHE image
        
        Parameters 
        ----------
        image : ndarray
            The image to apply the operation to

        Returns
        -------
        final_contrast
            An ndarray of of the same size as the input after the AHE and multiplication 
            operations have been applied
        '''

        try:
            AHE = exposure.equalize_adapthist(image)
            self.final_contrast = AHE * image
            return self.final_contrast
        except TypeError as e:
            print(f'This is not a valid type. Expected ndarray, but got {e}')
    

    def rescaled_intensity(self, image = None, vmin = .5, vmax = 99.5):
        ''' Rescales the intensity of the image using the intensities provided 
        
        If the arguments `vmin` and `vmax` aren't provided, the default 
        values of 0 and 255 are passed.
        
        Parameters 
        ----------
        image : ndarray
            The image to apply the operation to
        vmin : int, optional
            The minimum intensity value allowed for the image (default is 0)
        vmax : int, optional
            The maximum intensity value allowed for the image (default is 255)

        Returns
        -------
        final_contrast
            An ndarray of of the same size as the input after the rescaled intensity 
            operation has been applied
        '''
        
        try:
            vmin, vmax = np.percentile(image, q = (vmin, vmax))
            self.final_contrast = exposure.rescale_intensity(image, in_range = (vmin, vmax))

            return self.final_contrast
        except TypeError as e:
            print(f'This is not a valid type. Expected ndarray, but got {e}')


# -------------------- Mask Operations


    def multiotsu_mask(self, image = None, classes = 2):
        '''Performs the multiotsu mask operation from skimage
        
        If the argument `classes` isn't provided, the default 
        value of 2 is passed.
        
        Parameters 
        ----------
        image : ndarray
            The image to apply the operation to
        classes : int, optional
            The number of classes in the image (default is 2)

        Returns
        -------
        mask_morph
            an array with the same shaqpe as the input after the 
            mask has been applied
        '''

        try:
            thresh = filters.threshold_multiotsu(image = image, classes = classes)
            self.mask = image >= thresh
            self.mask_morph = self.mask
            self.mask_morph = np.where(self.cropped_skel, self.mask, 0)
            
            return self.mask_morph

        except TypeError as e:
            print(f'This is not a valid type. Expected ndarray, but got {e}')

    def otsu_mask(self, image = None):
        '''Performs the otsu mask operation from skimage
        
        Parameters 
        ----------
        image : ndarray
            The image to apply the operation to

        Returns
        -------
        mask_morph
            an array with the same shaqpe as the input after the 
            mask has been applied
        '''

        try:
            thresh = filters.threshold_otsu(image = image)
            self.mask = image >= thresh
            self.mask_morph = self.mask
            self.mask_morph = np.where(self.cropped_skel, self.mask, 0)
            return self.mask_morph

        except TypeError as e:
            print(f'This is not a valid type. Expected ndarray, but got {e}')

    def li_mask(self, image = None):
        '''Performs the li mask operation from skimage
        
        Parameters 
        ----------
        image : ndarray
            The image to apply the operation to

        Returns
        -------
        mask_morph
            an array with the same shaqpe as the input after the 
            mask has been applied
        '''

        try:
            thresh = filters.threshold_li(image = image)
            self.mask = image >= thresh
            self.mask_morph = self.mask
            self.mask_morph = np.where(self.cropped_skel, self.mask, 0)
            return self.mask_morph
        except TypeError as e:
            print(f'This is not a valid type. Expected ndarray, but got {e}')

    def yen_mask(self, image = None):
        '''Performs the yen mask operation
        
        Parameters 
        ----------
        image : ndarray
            The image to apply the operation to

        Returns
        -------
        mask_morph
            an array with the same shaqpe as the input after the 
            mask has been applied
        '''

        try:
            thresh = filters.threshold_yen(image = image)
            self.mask = image >= thresh
            self.mask_morph = self.mask
            self.mask_morph = np.where(self.cropped_skel, self.mask, 0)
            return self.mask_morph
        except TypeError as e:
            print(f'This is not a valid type. Expected ndarray, but got {e}')

# -------------------- Morphology Operations

    def default_morphology(self):
        '''Performs the default morphology operations: Binary Dilation and Binary Closing
        from skimage

        Returns
        -------
        mask_closing
            an array of the same shape as the input image. The final mask 
            after the morphology operations are performed
        final_mask
            an array of the same shape as the input image. The final mask 
            isolated only to the area within the skeleton
        '''

        try:
            mask_dilate = morphology.binary_dilation(self.mask)
            mask_closing = morphology.binary_closing(mask_dilate)
            self.final_mask = np.where(self.cropped_skel, mask_closing, 0)
            self.mask_morph = self.final_mask

            return mask_closing, self.final_mask

        except TypeError as e:
            print(f'This is not a valid type. Expected ndarray, but got {e}')

    def closing(self, mask = None):
        '''Performs the closing morphology operation from skimage

        Parameters
        ----------
        mask : ndarray
            The mask to perform the morph operation on

        Returns
        -------
        mask_morph
            The final mask of type ndarray after the morphology operation is performed
        '''
        try:
            self.mask_morph = morphology.binary_closing(mask)
            return self.mask_morph
        except TypeError as e:
            print(f'This is not a valid type. Expected ndarray, but got {e}')

    def opening(self, mask = None):
        '''Performs the opening morphology operation from skimage

        Parameters
        ----------
        mask : ndarray
            The mask to perform the morph operation on

        Returns
        -------
        mask_morph
            The final mask of type ndarray after the morphology operation is performed
        '''
        try:
            self.mask_morph = morphology.binary_opening(mask)
            return self.mask_morph
        except TypeError as e:
            print(f'This is not a valid type. Expected ndarray, but got {e}')

    def dilation(self, mask = None):
        '''Performs the dilation morphology operation from skimage

        Parameters
        ----------
        mask : ndarray
            The mask to perform the morph operation on

        Returns
        -------
        mask_morph
            The final mask of type ndarray after the morphology operation is performed
        '''

        try:
            self.mask_morph = morphology.binary_dilation(mask)
            return self.mask_morph
        except TypeError as e:
            print(f'This is not a valid type. Expected ndarray, but got {e}')

    def erosion(self, mask = None):
        '''Performs the erosion morphology operation from skimage

        Parameters
        ----------
        mask : ndarray
            The mask to perform the morph operation on

        Returns
        -------
        mask_morph
            The final mask of type ndarray after the morphology operation is performed
        '''
        try:
            self.mask_morph = morphology.binary_erosion(mask)
            return self.mask_morph
        except TypeError as e:
            print(f'This is not a valid type. Expected ndarray, but got {e}')
    

# -------------------- Label Operations

    def labels(self, mask = None):
        '''Generates labels based on the provided mask

        Parameters
        ----------
        mask : ndarray
            The mask to perform the morph operation on

        Returns
        -------
        boundaries
            an array of the same shape as the input

        label_image
            an array with labels of the same shape as the input. All
            connected areas are under one label
        '''

        try:
            label_image = measure.label(mask)
            boundaries = segmentation.find_boundaries(label_image)
            return boundaries, label_image

        except TypeError as e:
            print(f'This is not a valid type. Expected ndarray, but got {e}')

 

    def region_props(self, labels, intensity_image, properties):
        '''Generates a dictionary of properties requested for the labels
        provided

        Parameters
        ----------
        labels : ndarray
            The labeled image to generate the properties for
        intensity_image : ndarray
            The image to reference intensity values for
        properties : list
            A list of strings with the properties desired 

        Returns
        -------
        props
            a dictionary with the properties generated for each label
        '''
        
        try:
            props = measure.regionprops_table(labels, intensity_image, properties)
            return props
        except TypeError as e:
            print(f'This is not a valid type. Expected ndarray, but got {e}')