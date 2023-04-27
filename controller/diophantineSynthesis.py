# %%
import numpy as np
import control
from scipy import signal
from matplotlib import pyplot as plt

plt.rc('lines', linewidth=2)
plt.rc('axes', grid=True)
plt.rc('grid', linestyle='--')

# time
dt = 1e-2
t_start = 0
t_end = 10
t = np.arange(t_start, t_end, dt)


# System TF
k = -3.5
g = -9.81
s = control.tf('s')
plant = 179.91 / s ** 2  # short way
#plant_norm = plant / 200

# First Order Approximator (Controller)
controller = ((3/179.91)*s + (1/179.91)) / (s+3)
#controller_norm = controller / 10

#look at bode plot of L
# Open-loop transfer function
L = plant * controller
print(f'\nL(s) =', L)

# Roots of the closed-loop characteristic polynomial
char_poly_tf = control.tf(plant.den, 1) * control.tf(controller.den, 1) + control.tf(plant.num, 1) * control.tf(controller.num, 1)
char_poly = np.array(char_poly_tf.num).ravel()
char_poly_roots = np.roots(char_poly)
print(f'The roots of the characteristic polynomial are {char_poly_roots}\n')
print(f'The real part of the roots of the characteristic polynomial are {np.real(char_poly_roots)}\n')

# %% Sysetm interconnctions
# Feedback interconnection of plant and control
T = control.feedback(L, 1, -1)  # Complementary sensitivity transfer function
S = 1 - T  # Sensitivity transfer function
print(f'\nT(s) =', T)
print(f'\nS(s) =', S)

# %% Step response
# Step response of each system
t_b, y_b = control.step_response(plant, t)
t_T, y_T = control.step_response(T, t)

# Plot step response
fig, ax = plt.subplots()
ax.set_xlabel(r'$t$ (s)')
ax.set_ylabel(r'$y(t)$ (units)')
# Plot data
#ax.plot(t_b, y_b, label='$P_b(s)$', color='C2')
ax.plot(t_T, y_T, label='$T(s)$', color='C4')
ax.legend(loc='upper right')
fig.tight_layout()
# fig.savefig('figs/control_step_response.pdf')

# %% Impulse response
# Impulse response of each system
t_b, y_b = control.impulse_response(plant, t)
t_T, y_T = control.impulse_response(T, t)

# Plot impulse response
fig, ax = plt.subplots()
ax.set_xlabel(r'$t$ (s)')
ax.set_ylabel(r'$y(t)$ (units)')
# Plot data
#ax.plot(t_b, y_b, label='$P_b(s)$', color='C2')
ax.plot(t_T, y_T, label='$T(s)$', color='C4')
ax.legend(loc='upper right')
fig.tight_layout()
plt.show()
# %% Bode plots
# Calculate freq, magnitude, and phase
w_shared = np.logspace(-1, 3, 1000)
mag_a, phase_a, w_a = control.bode(L, w_shared, dB=True, deg=True, plot=True, label='L')
mag_a, phase_a, w_a = control.bode(T, w_shared, dB=True, deg=True, plot=True, label='T')
mag_a, phase_a, w_a = control.bode(S, w_shared, dB=True, deg=True, plot=True, label='S')
# fig.savefig('figs/control_Bode_plot_T.pdf')# %%

# %% Time-domaine forced response
# Square wave input
u = signal.square(2 * np.pi / 2 * t)

# Forced response of each system
t_a, y_a = control.forced_response(plant, t, u)

# Plot forced response
fig, ax = plt.subplots(2, 1)
ax[0].set_ylabel(r'$u(t)$ (units)')
ax[1].set_ylabel(r'$y(t)$ (units)')
# Plot data
ax[0].plot(t, u, label='input')
ax[1].plot(t_a, y_a, label='$P_b(s)$', color='C1')

for a in np.ravel(ax):
    a.set_xlabel(r'$t$ (s)')
    a.legend(loc='upper right')
fig.tight_layout()
plt.show()