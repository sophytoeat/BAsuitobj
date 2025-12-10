from PyQt5.QtCore import pyqtSlot

def init_shape_sliders(self):
    self.slider_list = [self.slider0, self.slider1, self.slider2, self.slider3, self.slider4,\
                                self.slider5, self.slider6, self.slider7, self.slider8, self.slider9]
    for i ,slider in enumerate(self.slider_list):
        slider.setRange(-50, 50)
        slider.setSingleStep(1)
        slider.valueChanged.connect(self.update_shape)

@pyqtSlot()
def update_shape(self):

    new_beta = self.beta.copy()
    for i in range(10):
        new_beta[i] = float(self.slider_list[i].value()) / 5
    self.beta = new_beta

    self.smpl.set_params(beta=self.beta)
    self.smpl_mesh.points = self.smpl.verts