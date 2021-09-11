from magicgui.widgets._bases import widget
from ImageProcessing_Program import ImageProcessing

import napari
from napari.qt.threading import thread_worker

from qtpy.QtWidgets import QLineEdit, QLabel, QWidget, QVBoxLayout, QPushButton
from qtpy.QtGui import QDoubleValidator


x = float(input('What is the x spacing?:' ))
y = float(input('What is the y spacing?:' ))
z = float(input('What is the z spacing?:' ))

spacing = [x,y,z]

viewer = napari.Viewer()

print('Only .tiff images will be read in for this program!')

image_Loc = str(input('What is the file location:'))
image_start = ImageProcessing(image_Loc)
image = image_start.image_read()

# function for what occurs when buttonAHE is clicked
# TODO: Make it parameter based so users can add which image they would like serve as a base
# And makes it so it defaults to the original image otherwise
def AHE_Clicked(): 
    new_AHE = image_start.Adaptive_Histo_Equal(image)
    viewer.add_image(
        new_AHE,
        scale = spacing,
    )

# function for what occurs when buttonRI is clicked
# TODO: Make it parameter based so users can add which image they would like serve as a base
# And makes it so it defaults to the original image otherwise

def RI_Clicked():
    new_RI = image_start.rescaled_intensity(image)
    viewer.add_image(
        new_RI,
        scale = spacing,
    )

# buttons in napari

widget = QWidget()
layout = QVBoxLayout()
widget.setLayout(layout)
result_label = QLabel()
line_edit = QLineEdit()
line_edit.setValidator(QDoubleValidator())
layout.addWidget(line_edit)
layout.addWidget(result_label)
viewer.window.add_dock_widget(widget)

buttonSTOP = QPushButton("STOP!")
viewer.window.add_dock_widget(buttonSTOP)
buttonRI = QPushButton('Rescaled Intensity Filter')
buttonAHE = QPushButton('Adaptive Histogram Equalization')
viewer.window.add_dock_widget(buttonRI)
viewer.window.add_dock_widget(buttonAHE)

buttonAHE.clicked.connect(AHE_Clicked)
buttonRI.clicked.connect(RI_Clicked)

print('Done reading image into Napari Viewer.')
print('The buttons on the side will allow you to choose what filters you would like applied to the image.')
print('When clicking on a button, you will be prompted in the command prompt to specify which layer you would like this filter \napplied to.')
print('If left blank, it will default to the original image.')
print('For reference, my order of steps for the image stored in the github is as follows:\n'
'PROCESSING STEPS\n'
'- Rescaled intensity\n'
'- Gaussian Blur\n'
'- Sobel Filter (edge detection/enhancement)\n'
'- MultiOtsu Threshold\n'
'MORPHOLOGICAL STEPS (POSTPROCESSING): These are used on the threshold to help fine tune it and clean up any small holes or really rough edges.\n'
'- Binary Closing\n'
'- Binary Opening\n'
'- Binary Dilation\n'
'- Binary Erosion\n')

napari.run()
