# %%
import numpy as np
import control
from scipy import signal
from matplotlib import pyplot as plt

#get discrete time controller
s = control.tf('s')
continuousController = ((3/34.5)*s + (1/34.5)) / (s+3)
ssController = control.tf2ss(continuousController)
discreteController = control.c2d(ssController, 0.06)
print(discreteController)
reference = 0

def feedbackLoop(currentState, currentOutput):
    currentError = currentOutput - reference

    nextState = discreteController.A @ np.reshape(currentError, (1,1)) + discreteController.B @ np.reshape(currentError, (1,1))
    controlEffort = discreteController.C @ nextState

    return nextState, controlEffort

print(feedbackLoop(0, 50))