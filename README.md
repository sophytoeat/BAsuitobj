# SMPL_shape_UI

## Installations
```
conda create --name SMPL python=3.10
conda activate SMPL
pip install pyqt5-tools
pip install pyvista[all]
pip install pyvistaqt
pip install scipy
pip install numpy==1.23
```
Trouble-shooting:

qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.
This application failed to start because no Qt platform plugin could be initialized. Reinstalling the application may fix this problem.
Available platform plugins are: eglfs, linuxfb, minimal, minimalegl, offscreen, vnc, wayland-egl, wayland, wayland-xcomposite-egl, wayland-xcomposite-glx, webgl, xcb.

```
sudo apt update
sudo apt install \
    libxcb1 libxcb-render0 libxcb-shape0 libxcb-xfixes0 \
    libxcb-image0 libxcb-keysyms1 libxcb-icccm4 libxcb-sync1 \
    libxcb-randr0 libxcb-util1 libxcb-xinerama0 libxcb-cursor0 \
    libxkbcommon-x11-0 libxrender1 libx11-xcb1
```

### Project Structure
```
project_root/
├── SMPL_models/
│   ├── basicModel_f_lbs_10_207_0_v1.0.0.pkl
│   ├── basicModel_m_lbs_10_207_0_v1.0.0.pkl
│   ├── basicModel_neutral_lbs_10_207_0_v1.0.0.pkl
│   ├── J_regressor_extra.npy
│   └── J_regressor_h36m.npy
├── SMPL_Anthropometry
├── UI_utils/
├── utils/
├── main.py
└── README.md
```
