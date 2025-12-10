import os
from PyQt5.QtCore import pyqtSlot

@pyqtSlot()
def export_smpl(self):

    filename = self.NameExport.toPlainText().strip()
    if not filename:
        filename = "current_shape"
    filename += ".obj"

    full_path = os.path.join(self.args.output_path, filename)
    self.smpl.save_to_obj(full_path)
