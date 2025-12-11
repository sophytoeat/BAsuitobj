
from typing import List, Dict
import numpy as np
import trimesh
from pprint import pprint
import os
import argparse

from SMPL_Anthropometry.measurement_definitions import *
from SMPL_Anthropometry.utils import *
from SMPL_Anthropometry.landmark_definitions import *
from SMPL_Anthropometry.joint_definitions import *

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.smpl_np import SMPLModel


def get_smpl_model_path(gender):
    '''
    Get path to SMPL model file based on gender.
    :param gender: str - MALE, FEMALE, or NEUTRAL

    Returns:
    :param model_path: str - path to the pkl file
    '''
    # Try both locations - first check if SMPL_models exists (used by UI),
    # otherwise use SMPL_Anthropometry/data/smpl (current location)

    # Map gender to model file names for different locations
    ui_model_map = {
        'MALE': 'basicModel_m_lbs_10_207_0_v1.0.0.pkl',
        'FEMALE': 'basicModel_f_lbs_10_207_0_v1.0.0.pkl',
        'NEUTRAL': 'basicmodel_m_lbs_10_207_0_v1.0.0.pkl'
    }

    data_model_map = {
        'MALE': 'SMPL_NEUTRAL.pkl',  # Use neutral for male if not available
        'FEMALE': 'SMPL_FEMALE.pkl',
        'NEUTRAL': 'SMPL_NEUTRAL.pkl'
    }

    gender_upper = gender.upper()

    model_path = os.path.join('SMPL_models', ui_model_map.get(gender_upper, ui_model_map['NEUTRAL']))
    if os.path.exists(model_path):
        return model_path

def set_shape(model, shape_coefs):
    '''
    Set shape of body model.
    :param model: smplx body model
    :param shape_coefs: torch.tensor dim (10,)

    Return
    shaped smplx body model
    '''
    shape_coefs = shape_coefs.to(torch.float32)
    return model(betas=shape_coefs, return_verts=True)

def create_model(model_type, model_root, gender, num_betas=10, num_thetas=24):
    '''
    Create SMPL/SMPLX/etc. body model
    :param model_type: str of model type: smpl, smplx, etc.
    :param model_root: str of location where there are smpl/smplx/etc. folders with .pkl models
                        (clumsy definition in smplx package)
    :param gender: str of gender: MALE or FEMALE or NEUTRAL
    :param num_betas: int of number of shape coefficients
                      requires the model with num_coefs in model_root
    :param num_thetas: int of number of pose coefficients
    
    Return:
    :param smplx body model (SMPL, SMPLX, etc.)
    '''
    
    #body_pose = torch.zeros((1, (num_thetas-1) * 3))
    
    return smplx.create(model_path=model_root,
                        model_type=model_type,
                        gender=gender, 
                        use_face_contour=False,
                        num_betas=num_betas,
                        #body_pose=body_pose,
                        ext='pkl')



class Measurer():
    '''
    Measure a parametric body model defined either.
    Parent class for Measure{SMPL,SMPLX,..}.

    All the measurements are expressed in cm.
    '''

    def __init__(self):
        self.verts = None
        self.faces = None
        self.joints = None
        self.gender = None

        self.measurements = {}
        self.height_normalized_measurements = {}
        self.labeled_measurements = {}
        self.height_normalized_labeled_measurements = {}
        self.labels2names = {}

    def from_verts(self):
        pass

    def from_body_model(self):
        pass

    def measure(self, 
                measurement_names: List[str]
                ):
        '''
        Measure the given measurement names from measurement_names list
        :param measurement_names - list of strings of defined measurements
                                    to measure from MeasurementDefinitions class
        '''

        for m_name in measurement_names:
            if m_name not in self.all_possible_measurements:
                print(f"Measurement {m_name} not defined.")
                pass

            if m_name in self.measurements:
                pass

            if self.measurement_types[m_name] == MeasurementType().LENGTH:

                value = self.measure_length(m_name)
                self.measurements[m_name] = value

            elif self.measurement_types[m_name] == MeasurementType().CIRCUMFERENCE:

                value = self.measure_circumference(m_name)
                self.measurements[m_name] = value

            elif self.measurement_types[m_name] == MeasurementType().DERIVED:

                value = self.measure_derived(m_name)
                self.measurements[m_name] = value

            else:
                print(f"Measurement {m_name} not defined")

    def measure_length(self, measurement_name: str):
        '''
        Measure distance between 2 landmarks
        :param measurement_name: str - defined in MeasurementDefinitions

        Returns
        :float of measurement in cm
        '''

        measurement_landmarks_inds = self.length_definitions[measurement_name]

        landmark_points = []
        for i in range(2):
            if isinstance(measurement_landmarks_inds[i],tuple):
                # if touple of indices for landmark, take their average
                lm = (self.verts[measurement_landmarks_inds[i][0]] + 
                          self.verts[measurement_landmarks_inds[i][1]]) / 2
            else:
                lm = self.verts[measurement_landmarks_inds[i]]
            
            landmark_points.append(lm)

        landmark_points = np.vstack(landmark_points)[None,...]

        return self._get_dist(landmark_points)

    @staticmethod
    def _get_dist(verts: np.ndarray) -> float:
        '''
        The Euclidean distance between vertices.
        The distance is found as the sum of each pair i 
        of 3D vertices (i,0,:) and (i,1,:) 
        :param verts: np.ndarray (N,2,3) - vertices used 
                        to find distances
        
        Returns:
        :param dist: float, sumed distances between vertices
        '''

        verts_distances = np.linalg.norm(verts[:, 1] - verts[:, 0],axis=1)
        distance = np.sum(verts_distances)
        distance_cm = distance * 100 # convert to cm
        return distance_cm
    
    def measure_circumference(self, 
                              measurement_name: str, 
                              ):
        '''
        Measure circumferences. Circumferences are defined with 
        landmarks and joints - the measurement is found by cutting the 
        SMPL model with the  plane defined by a point (landmark point) and 
        normal (vector connecting the two joints).
        :param measurement_name: str - measurement name

        Return
        float of measurement value in cm
        '''

        measurement_definition = self.circumf_definitions[measurement_name]
        circumf_landmarks = measurement_definition["LANDMARKS"]
        circumf_landmark_indices = [self.landmarks[l_name] for l_name in circumf_landmarks]
        circumf_n1, circumf_n2 = self.circumf_definitions[measurement_name]["JOINTS"]
        circumf_n1, circumf_n2 = self.joint2ind[circumf_n1], self.joint2ind[circumf_n2]
        
        plane_origin = np.mean(self.verts[circumf_landmark_indices,:],axis=0)
        plane_normal = self.joints[circumf_n1,:] - self.joints[circumf_n2,:]

        mesh = trimesh.Trimesh(vertices=self.verts, faces=self.faces)

        # new version            
        slice_segments, sliced_faces = trimesh.intersections.mesh_plane(mesh, 
                                plane_normal=plane_normal, 
                                plane_origin=plane_origin, 
                                return_faces=True) # (N, 2, 3), (N,)
        
        slice_segments = filter_body_part_slices(slice_segments,
                                                 sliced_faces,
                                                 measurement_name,
                                                 self.circumf_2_bodypart,
                                                 self.face_segmentation)
        
        slice_segments_hull = convex_hull_from_3D_points(slice_segments)

        return self._get_dist(slice_segments_hull)

    def measure_derived(self, measurement_name: str):
        '''
        Compute derived measurements from existing measurements.
        :param measurement_name: str - measurement name

        Return
        float of measurement value in cm
        '''

        if measurement_name not in self.derived_definitions:
            print(f"Derived measurement {measurement_name} not defined")
            return None

        # Get the definition for this derived measurement
        derived_def = self.derived_definitions[measurement_name]

        # Check if required measurements are available
        required_measurements = derived_def["requires"]
        for req_measure in required_measurements:
            if req_measure not in self.measurements:
                # Measure the required measurement if not already done
                self.measure([req_measure])

        # Compute and return the derived measurement
        compute_func = derived_def["function"]
        return compute_func(self.measurements)

    def height_normalize_measurements(self, new_height: float):
        ''' 
        Scale all measurements so that the height measurement gets
        the value of new_height:
        new_measurement = (old_measurement / old_height) * new_height
        NOTE the measurements and body model remain unchanged, a new
        dictionary height_normalized_measurements is created.
        
        Input:
        :param new_height: float, the newly defined height.

        Return:
        self.height_normalized_measurements: dict of 
                {measurement:value} pairs with 
                height measurement = new_height, and other measurements
                scaled accordingly
        '''
        if self.measurements != {}:
            old_height = self.measurements["height"]
            for m_name, m_value in self.measurements.items():
                norm_value = (m_value / old_height) * new_height
                self.height_normalized_measurements[m_name] = norm_value

            if self.labeled_measurements != {}:
                for m_name, m_value in self.labeled_measurements.items():
                    norm_value = (m_value / old_height) * new_height
                    self.height_normalized_labeled_measurements[m_name] = norm_value

    def label_measurements(self,set_measurement_labels: Dict[str, str]):
        '''
        Create labeled_measurements dictionary with "label: x cm" structure
        for each given measurement.
        NOTE: This overwrites any prior labeling!
        
        :param set_measurement_labels: dict of labels and measurement names
                                        (example. {"A": "head_circumference"})
        '''

        if self.labeled_measurements != {}:
            print("Overwriting old labels")

        self.labeled_measurements = {}
        self.labels2names = {}

        for set_label, set_name in set_measurement_labels.items():
            
            if set_name not in self.all_possible_measurements:
                print(f"Measurement {set_name} not defined.")
                pass

            if set_name not in self.measurements.keys():
                self.measure([set_name])

            self.labeled_measurements[set_label] = self.measurements[set_name]
            self.labels2names[set_label] = set_name


class MeasureSMPL(Measurer):
    '''
    Measure the SMPL model defined either by the shape parameters or
    by its 6890 vertices. 

    All the measurements are expressed in cm.
    '''

    def __init__(self):
        
        super().__init__()

        self.model_type = "smpl"

        # Load a reference model to get faces
        # Use FEMALE model by default for getting faces (same across all genders)
        ref_model_path = get_smpl_model_path('FEMALE')
        ref_model = SMPLModel(ref_model_path)
        self.faces = ref_model.faces

        # Load face segmentation from SMPL_Anthropometry/data/smpl
        face_segmentation_path = os.path.join("SMPL_models",
                                              "smpl_body_parts_2_faces.json")
        self.face_segmentation = load_face_segmentation(face_segmentation_path)

        self.landmarks = SMPL_LANDMARK_INDICES
        self.measurement_types = MEASUREMENT_TYPES
        self.length_definitions = SMPLMeasurementDefinitions().LENGTHS
        self.circumf_definitions = SMPLMeasurementDefinitions().CIRCUMFERENCES
        self.circumf_2_bodypart = SMPLMeasurementDefinitions().CIRCUMFERENCE_TO_BODYPARTS
        self.derived_definitions = SMPLMeasurementDefinitions().DERIVED
        self.all_possible_measurements = SMPLMeasurementDefinitions().possible_measurements

        self.joint2ind = SMPL_JOINT2IND
        self.num_joints = SMPL_NUM_JOINTS

        self.num_points = 6890

    def from_verts(self, verts: np.ndarray):
        '''
        Construct body model from only vertices.
        :param verts: np.ndarray (6890,3) of SMPL vertices
        '''

        verts = verts.squeeze()
        error_msg = f"verts need to be of dimension ({self.num_points},3)"
        assert verts.shape == (self.num_points, 3), error_msg

        # Get joint regressor from a reference model
        ref_model_path = get_smpl_model_path('NEUTRAL')
        ref_model = SMPLModel(ref_model_path)
        joint_regressor = ref_model.J_regressor

        joints = np.matmul(joint_regressor, verts)
        self.joints = joints
        self.verts = verts

    def from_body_model(self, gender: str, shape: np.ndarray):
        '''
        Construct body model from given gender and shape params
        of SMPL model.
        :param gender: str, MALE or FEMALE or NEUTRAL
        :param shape: np.ndarray, (10,) or (1,10) beta parameters
                                    for SMPL model
        '''

        # Load the appropriate SMPL model
        model_path = get_smpl_model_path(gender)
        model = SMPLModel(model_path)

        # Ensure shape is 1D array of length 10
        shape = np.array(shape).flatten()
        assert len(shape) == 10, f"Shape must be length 10, got {len(shape)}"

        # Set shape parameters (pose remains at zero/T-pose)
        model.set_params(beta=shape)

        self.verts = model.verts
        self.joints = model.J
        self.gender = gender


class MeasureBody():
    def __new__(cls, model_type):
        model_type = model_type.lower()
        if model_type == 'smpl':
            return MeasureSMPL()
        else:
            raise NotImplementedError(f"Model type '{model_type}' not supported. Only 'smpl' is supported.")