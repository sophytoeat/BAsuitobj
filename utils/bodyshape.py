from PyQt5.QtCore import pyqtSlot

def init_shape_sliders(self):
    self.slider_list = [self.slider0, self.slider1, self.slider2, self.slider3, self.slider4,\
                                self.slider5, self.slider6, self.slider7, self.slider8, self.slider9]
    for i ,slider in enumerate(self.slider_list):
        slider.setRange(-self.args.slider_scale, self.args.slider_scale)
        slider.setSingleStep(1)
        slider.valueChanged.connect(self.update_shape)

@pyqtSlot()
def update_shape(self):

    sender = self.sender()
    if sender in self.slider_list:
        slider_index = self.slider_list.index(sender)
        # Only update the specific beta value that corresponds to the changed slider
        self.beta[slider_index] = float(sender.value()) / self.args.slider_scale

    self.smpl.set_params(beta=self.beta)
    self.smpl_mesh.points = self.smpl.verts