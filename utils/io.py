import os
from PyQt5.QtCore import pyqtSlot
from utils.measurement import Body3D

from pprint import pprint
from SMPL_Anthropometry.measure import MeasureBody
from SMPL_Anthropometry.measurement_definitions import STANDARD_LABELS

@pyqtSlot()
def export_smpl(self):

    filename = self.NameExport.toPlainText().strip()
    if not filename:
        filename = "current_shape"
    filename += ".obj"

    full_path = os.path.join(self.args.output_path, filename)
    self.smpl.save_to_obj(full_path)


@pyqtSlot()
def print_params(self):
    print("====== Params ======")
    print(self.beta)


@pyqtSlot()
def print_measures(self):

    measurer = MeasureBody('smpl')
    measurer.from_body_model(gender='FEMALE', shape=self.beta)
    measurement_names = measurer.all_possible_measurements
    measurer.measure(measurement_names)
    measurer.label_measurements(STANDARD_LABELS)

    body_measurements = {
        'A': measurer.measurements['height'],
        'B': measurer.measurements['chest circumference'],
        'C': measurer.measurements['hip circumference'],
        'D': measurer.measurements['waist circumference'],
        'E': measurer.measurements['thigh left circumference'],
        'F': measurer.measurements['outside leg height'],
        'G': measurer.measurements['inside leg height'],
        'H': measurer.measurements['shoulder to crotch height'],
        'I': measurer.measurements['shoulder breadth'],
    }

    print("====== Measures ======")
    print(body_measurements)