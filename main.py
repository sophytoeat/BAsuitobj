import os
import sys
import torch
import argparse
import numpy as np
from scipy.spatial.transform import Rotation as R
import pyvista as pv
from pyvistaqt import QtInteractor
from PyQt5 import QtWidgets, uic, QtCore
from utils.smpl_np import SMPLModel

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, args):
        super().__init__()
        self.args = args

        # Load UI from Designer
        uic.loadUi("./UI_utils/MainWindow.ui", self)

        # Replace QWidget placeholder with QtInteractor
        self.plotter = QtInteractor(self.canvas3D)
        layout = QtWidgets.QVBoxLayout(self.canvas3D)
        layout.addWidget(self.plotter.interactor)
        #self.plotter.add_axes()
        #self.plotter.set_viewup([0, 1, 0], reset=False)

        # Load your SMPL OBJ file
        self.smpl = SMPLModel('./SMPL_models/basicModel_f_lbs_10_207_0_v1.0.0.pkl')

        self.current_pose = np.zeros([24,3])
        self.current_pose[16, 2] = 5.6
        self.current_pose[17, 2] = -5.6
        original_rotation = R.from_rotvec(self.current_pose[0,:])
        x_axis_rotation = R.from_rotvec(np.pi/2 * np.array([1, 0, 0]))
        z_axis_rotation = R.from_rotvec(np.pi / 2 * np.array([0, 0, 1]))
        combined_rotation = z_axis_rotation * x_axis_rotation * original_rotation
        self.current_pose[0,:] = combined_rotation.as_rotvec()
        self.smpl.set_params(pose=self.current_pose)

        faces_pv = np.hstack([
            np.full((self.smpl.faces.shape[0], 1), 3),  # column of 3s
            self.smpl.faces]).astype(np.int64).ravel()
        self.smpl_mesh = pv.PolyData(self.smpl.verts, faces_pv)

        self.mesh_actor = self.plotter.add_mesh(
            self.smpl_mesh, color="lightgray", show_edges=False,
            opacity=1, pickable=False
        )
        self.plotter.reset_camera()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=True, description="UI for SMPL shape manipulation.")
    parser.add_argument('--output_path', type=str, default="./outputs",
                        help='The folder to hold UI log files.')
    args = parser.parse_args()

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(args)
    window.show()
    sys.exit(app.exec_())