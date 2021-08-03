# Image Segmentation
#### Contribution by Ashley Hardy

This folder contains the following files:

- Bestman_Lab_Image_Segmentation_Code.ipynb
- Example_Dec9th_Image.png
- cropped_Projections_of_Dec9_P117_mlsEGFP_uasRFP_D3T4MFLrotcr.Blind_fused1.tif
- Mask Comparisons

## Bestman Lab Code

The goal of this project is to create a semi-automated image segmentation program to aid in analysis of cell images taken in the Bestman Lab. The analysis focuses on segmenting the mitochondria along the radial length. Several image segmentation methods were used and tested on the example file "cropped_Projections_of_Dec9_P117_mlsEGFP_uasRFP_D3T4MFLrotcr.Blind_fused1.tif". All code is based in Python and primarily uses skimage for image processing steps. Matplotlib is used for viewing graphs and Napari is used for viewing the images following the image processing operations in a 3D space.

Image Processing Steps (in order):

- Rescaled Intensity
- Sobel Filter
- Gaussian Blur
- Multiotsu Mask
- Morphological steps: Binary Closing, Opening, Dilation, and Erosion

The resulting image after these steps can be seen in Example_Dec9th_Image.png.![Example_Dec9th_Image](https://user-images.githubusercontent.com/88122234/127952264-91d76d29-9c1a-461e-9ed3-3ee512f5705f.png)



Various methods were compared in the main file. For exposure, rescaled intensity and adaptive histogram equalization were compared, with the rescaled intensity being used for the rest of the image processing. The histograms for the original image, the rescaled intensity image, and adaptive histogram equalization image can be found in the Jupyter Notebook. 

Comparisons between the otsu mask and multiotsu mask were also drawn, with the multiotsu mask yielding better results for the image. To improve the mask, we used a combination of morphological steps (listed above). The resulting mask plus the points on the image are found in the Example_Dec9th_Image.png file.

Future steps include further improving the quality and specificity of the segmentation in addition to having just the region of interest being the in the image files.  Furthermore, segmentation is improved, extract the data from the segmentation.
