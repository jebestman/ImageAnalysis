import numpy as np
import napari  
from skimage import filters, morphology, measure, exposure, segmentation, restoration, feature, util
from scipy import ndimage as ndi

class Image_Processing():

    def __init__(self, image, skeleton, spacing, viewer):
        self.image = image
        self.skeleton = skeleton
        self.spacing = spacing
        self.viewer = viewer

    def add_to_viewer(self, image_name, layer_name):
        self.viewer.add_image(
            image_name,
            name = layer_name,
            scale = self.spacing
        )
    

    def image_analysis(self):
        def __skeleton():
            for i in range(0,10):
                skel = morphology.dilation(self.skeleton)
                i+=1
                
            median_skel = filters.median(skel)
            return median_skel
        
        skeleton = __skeleton()
        
        p, y, x = np.where(skeleton)
        p1 = min(p)
        p2 = max(p)
        row1 = min(x)
        row2 = max(x)
        col1 = min(y)
        col2 = max(y)
        ROI = self.image[p1:p2, col1:col2, row1:row2]
        skele = skeleton[p1:p2, col1:col2, row1:row2]
        self.add_to_viewer(ROI, 'ROI')
        self.add_to_viewer(skele, 'Skeleton')
        
        selem = morphology.cube(3)

        # median filter
        median = filters.median(ROI, selem = selem)
        median = util.img_as_float(median)
        self.add_to_viewer(median, 'median')
        
        # background subtraction
        background = filters.gaussian(median, 50.0)
        self.add_to_viewer(background, 'background')
        subtract = median - background
        self.add_to_viewer(subtract, 'subtract')

        AHE = exposure.equalize_adapthist(subtract)
        multiplied = AHE * subtract
        self.add_to_viewer(multiplied, 'multiplied')

        # thresholding
        thresh = filters.threshold_multiotsu(image = multiplied, classes = 2)
        otsu = multiplied >= thresh
        self.add_to_viewer(otsu, 'otsu_mask')

        # morphological operations
        otsu_open = morphology.binary_dilation(otsu)
        otsu_closing = morphology.binary_closing(otsu_open)
        self.add_to_viewer(otsu_closing, 'otsu_closing')
        # adding labels and points to the image
        cleared = segmentation.clear_border(otsu_closing)
        label_image = measure.label(cleared)
        boundaries = segmentation.find_boundaries(label_image)
        self.viewer.add_labels(
        boundaries,
        scale=spacing,
        )
        
        return ROI, label_image
