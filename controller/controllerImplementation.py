# %%
import numpy as np
import control
from scipy import signal
from matplotlib import pyplot as plt

#get discrete time controller
s = control.tf('s')
continuousController = (8341*s) / (s**2 + 170*s + 7000)
continuousControllerNewK = (3575*s)/ (s**2 + 170*s + 7000)
continuousControllerNewKPade = (-3575*s**2 + 7.149*10**5*s) / (s**3 + 370*s**2 + 4.345*10**4*s + 1.645*10**6)
continuousControllerAggressivePade = (-2626*s**2 + 7.149*10**5*s) / (s**3 + 370*s**2 + 4.345*10**4*s + 1.645*10**6)
tau_delay = 1/50
kp = 350
kd = 0.01

continuousControllerPD = kp + kd * (s/ (tau_delay*(s+1)))
print(continuousControllerPD)
reference = 0

# DT controller
sample_time = 0.1  # seconds
C_d = continuousControllerNewK.sample(sample_time, 'zoh')
C_d_ss = control.tf2ss(np.array(C_d.num).ravel(), np.array(C_d.den).ravel())
A_d, B_d, C_d, D_d = C_d_ss.A, C_d_ss.B, C_d_ss.C, C_d_ss.D
print("discretized:", A_d, B_d, C_d, D_d)


def feedbackLoop(currentState, currentOutput):
    currentError = currentOutput - reference

    nextState = A_d * currentState + B_d * currentError
    controlEffort = C_d @ nextState

    return nextState, controlEffort