import torch
from pprint import pprint
from measure import MeasureBody
from measurement_definitions import STANDARD_LABELS
import numpy as np

beta_uniform = torch.FloatTensor([[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]])
beta_thin = torch.FloatTensor([[0.0, 1.500000, -0.004604, 0.0, 0.0, -0.005301, 0.001116, 0.0, -0.002779, 0.002407]])
beta_normal = torch.FloatTensor([[0.0, 0.0, -0.00460438, 0.0, -0.25, -0.0053011, 0.00111622, 0.0, -0.00277905, 0.00240685]])
beta_fat = torch.FloatTensor([[0.0, -2.500000, -0.004604, -0.500000, 0.0, -0.005301, 0.001116, 0.0, -0.002779, 0.002407]])

measurer = MeasureBody('smpl')

beta = (beta_normal + beta_fat)/2
#beta = torch.zeros((1, 10), dtype=torch.float32)
measurer.from_body_model(gender='FEMALE', shape=beta)

measurement_names = measurer.all_possible_measurements
measurer.measure(measurement_names)
measurer.label_measurements(STANDARD_LABELS)
#pprint(measurer.measurements)

my_measures = {
'A': measurer.measurements['height'],
'B': measurer.measurements['chest circumference'],
'C': measurer.measurements['hip circumference'],
'D': measurer.measurements['waist circumference'],
'E': measurer.measurements['thigh left circumference'],
'F': measurer.measurements['height']/2+0.05,
'G': measurer.measurements['inside leg height'],
'H': measurer.measurements['shoulder to crotch height'],
'I': measurer.measurements['shoulder breadth'],
}

pprint(my_measures)