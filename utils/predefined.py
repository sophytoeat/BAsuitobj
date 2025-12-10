import numpy as np
from PyQt5.QtCore import pyqtSlot

@pyqtSlot()
def set_thin(self):

    self.beta = np.array([0.0, 1.500000, -0.004604, 0.0, 0.0, -0.005301, 0.001116, 0.0, -0.002779, 0.002407])

    for i, slider in enumerate(self.slider_list):
        slider.blockSignals(True)
        slider.setValue(int(round(self.beta[i] * self.args.slider_scale)))
        slider.blockSignals(False)

    self.smpl.set_params(beta=self.beta)
    self.smpl_mesh.points = self.smpl.verts


@pyqtSlot()
def set_standard(self):

    self.beta = np.array([0.0, 0.0, -0.00460438, 0.0, -0.25, -0.0053011, 0.00111622, 0.0, -0.00277905, 0.00240685])

    for i, slider in enumerate(self.slider_list):
        slider.blockSignals(True)
        slider.setValue(int(round(self.beta[i] * self.args.slider_scale)))
        slider.blockSignals(False)

    self.smpl.set_params(beta=self.beta)
    self.smpl_mesh.points = self.smpl.verts


@pyqtSlot()
def set_inter(self):

    self.beta = (np.array([0.0, 0.0, -0.00460438, 0.0, -0.25, -0.0053011, 0.00111622, 0.0, -0.00277905, 0.00240685])
                 +
                 np.array([0.0, -2.500000, -0.004604, -0.500000, 0.0, -0.005301, 0.001116, 0.0, -0.002779, 0.002407]))/2

    for i, slider in enumerate(self.slider_list):
        slider.blockSignals(True)
        slider.setValue(int(round(self.beta[i] * self.args.slider_scale)))
        slider.blockSignals(False)

    self.smpl.set_params(beta=self.beta)
    self.smpl_mesh.points = self.smpl.verts


@pyqtSlot()
def set_fat(self):

    self.beta = np.array([0.0, -2.500000, -0.004604, -0.500000, 0.0, -0.005301, 0.001116, 0.0, -0.002779, 0.002407])

    for i, slider in enumerate(self.slider_list):
        slider.blockSignals(True)
        slider.setValue(int(round(self.beta[i] * self.args.slider_scale)))
        slider.blockSignals(False)

    self.smpl.set_params(beta=self.beta)
    self.smpl_mesh.points = self.smpl.verts