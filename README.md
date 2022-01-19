# Image Analysis
Authors: A. Hardy, A. Ramakrishnan, J. Bestman

## Dependencies
matplotlib, numpy, pandas, scipy, scikit-image, napari>=0.4.12, xlrd, plotly, xlsxwriter

## Image Processing
A. Hardy
Provides a semi-automated image analysis script for neural progenitor cells by reading in the folder with the image contained. File contents must include:
```
1. GFP image
2. Skeleton file
3. Red fluorescence
4. Log file
5. Tissue image file
6. Traces file
```
The GFP image and skeleton image must remain in this order (first and second within the folder respectively). The files after (3-6) do not have to remain in that order but it keeps files consistent.

The **main.py** file is an example usage of the image processing python script. The image processing scrip returns the labels and the cropped GFP image to only the radial process. The napari viewer can be interacted with after to obtain necessary images as desired. 

It is recommended that you close the napari viewer after running each image folder as a new one will be initiated with each run of main.py. 

Image is cropped to conserve memory and also focus the program on the cell of interest. The skeleton file isolates results to the radial process. 

To run main.py through the command line:
```
python main.py
```

## Image Intensities Calculator
A. Ramakrishnan

Calculates the cumulative relative intensity for the raw intensity signals. Takes into account quiescent and dividing cells. 

The program will ask how many cells are in the spreadsheet and calculate the cumulative relative mitochondrial intensities within a large dataset. 

The program will provide several graph options to view the data:
- Plot each cell and its cumulative relative intensities in its own color
- Plot all quiescent and dividing cells in their own colors
- Plot all cells from the same cell date in one color
- Plot average intensities per 10% distance for all cells of the same data
- Plot average intensities per 10% distance for on cell over many dates.

Each option may require some sub configuration. Will return figures and an excel worksheet of the data if desired.

To run this program through the command line do the following:
```
python Image_Intensities_Calculator.py
```
This will prompt the user to provide the file path for the folder and then the filename. 
