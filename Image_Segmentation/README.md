# Image Segmentation
#### Contribution by Ashley Hardy

This folder contains the following files:

- Bestman_Lab_Image_Segmentation_Code.ipynb
- Image_Processing_Code.py 
- Example_Dec9th_Image.png
- cropped_Projections_of_Dec9_P117_mlsEGFP_uasRFP_D3T4MFLrotcr.Blind_fused1.tif
- Mask Comparisons

## Bestman Lab Code

The goal of this project is to create a semi-automated image segmentation program to aid in analysis of cell images taken in the Bestman Lab. The analysis focuses on segmenting the mitochondria along the radial length. Several image segmentation methods were used and tested on the example file. All code is based in Python and primarily uses skimage for image processing steps. Matplotlib is used for viewing graphs and Napari is used for viewing the images following the image processing operations in a 3D space.

### Image Processing Steps (in order):

- Rescaled Intensity
- Denoise Wavelet with BayesShrink method
- Median Filter
- Sobel Filter
- Adaptive Histogram Equalization multiplied to the sobel filter image
- Skimage Unsharp
- Skeleton mask dilated to width 20px
- Skeleton mask multiplied to the Unsharp Image to have just the radial process
- Multiotsu Mask
- Morphological steps: Binary Closing, Opening, Dilation, and Erosion
- Points and data are extracted

The sigma for the Denoise Wavelet is calcualted with skimage's built in sigma_estimate tool. The CLAHE mutlitiplied to the sobel filter enhances the contrast of the image. The darker areas surrounded by dark neighbords become darker and the brighter spots surrounded by bright neighbors become enhanced as well. Data is extracted from skimage's built in regionprops feature. 
The skeleton file is created from the .traces file generated in ImageJ which follows along the radial process of the neuron. This step isolates the multiotsu mask to only look in the area of the skeleton mask. 

The resulting image after these steps can be seen in Example_Image.png.![Example_Image](https://github.com/jebestman/ImageAnalysis/blob/ef513b65dd1c0d910aa4f0294e99c994506ed51c/Image_Segmentation/Example_Image%20File.png)



Various methods were compared in the main file. For exposure, rescaled intensity and adaptive histogram equalization were compared, with the rescaled intensity being used for the rest of the image processing. The histograms for the original image, the rescaled intensity image, and adaptive histogram equalization image can be found in the Jupyter Notebook. 

Comparisons between the otsu mask and multiotsu mask were also drawn, with the multiotsu mask yielding better results for the image. To improve the mask, we used a combination of morphological steps (listed above).
