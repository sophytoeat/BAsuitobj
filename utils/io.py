import os
from PyQt5.QtCore import pyqtSlot
from utils.measurement import Body3D

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
    measure_body = Body3D(self.smpl.verts, self.smpl.faces)
    body_measurements = measure_body.getMeasurements()

    print("====== Measures ======")
    print(body_measurements)