"""Internal model control.
Inspired by Skogestand and Postlethwait, Sec. 2.7
James Forbes
2022/03/21
"""
# %%
# Libraries
import numpy as np
from matplotlib import pyplot as plt
import control
from scipy import signal
import pathlib
# %%
# Plotting parameters
plt.rc('text', usetex=False)
plt.rc('font', family='serif', size=14)
plt.rc('lines', linewidth=2)
plt.rc('axes', grid=True)
plt.rc('grid', linestyle='--')
path = pathlib.Path('figs') 
path.mkdir(exist_ok=True)
# %%
# Functions
def pade(tau, K):
    """Compute Pade approximation."""
# Laplace variable s
    s = control.tf('s')
    num = 0
    den = 0
    for k in range(K + 1):
        num = num + (-tau * s / 2)**k / np.math.factorial(k)
        den = den + (tau * s / 2)**k / np.math.factorial(k)
    return num / den
# %%
# Common parameters
# Lapplace variable
s = control.tf('s')
# Bode plot
N_w = 500
w_shared = np.logspace(-2, 2, N_w)
# time
dt = 1e-3
t_start = 0
t_end = 5
t = np.arange(t_start, t_end, dt)
# %%
# Desired bandwidth
w_ref_max = (1 / 0.5) * 2 * np.pi  # X cycles/s * 2 * np.pi to get rad/s
gamma_r_dB = 0
# %%
# Create plant TF
tau_delay = 1/35  # This delay emulates the 'zoh' of discritization
kg = 1/1.5 * 9.81
#if pade is desired (a tau constant delay)
P = pade(tau_delay, 1) * kg / s**2
P = 5.24 * kg / s**2
# %%
# Internal model control design
P_m = 5.24 * kg / s**2
P_n = pade(tau_delay, 1)
#P_n = 1
tau_c = 1 / (30)  # inverse of desired cross over frequency
# F = 1 / (tau_c * s + 1) / ((tau_c / 2) * s + 1)
F = 1 / (tau_c * s + 1)**2  # must be order 2 or greater else C is improper
C = control.minreal(F * P_n / (P_m * (1 - F * P_n))) / (s / 100 + 1)
# C = (F / (P_m * (1 - F * P_n)))
'''
# If the controller must be truncated.
C_ss = control.tf2ss(np.array(C.num).ravel(), np.array(C.den).ravel()) 
Cr_ss = control.modelsimp.balred(C_ss, 4, method='truncate')
Cr = control.ss2tf(Cr_ss.A, Cr_ss.B, Cr_ss.C, Cr_ss.D)
C = Cr
'''
L = control.minreal(P * C)
# %%
# Roots of characteristic polynomial
T = control.minreal(control.feedback(L))
T_num = np.array(T.num).ravel()
T_den = np.array(T.den).ravel()
T = control.minreal(control.tf(T_num / T_den[0], T_den / T_den[0]))
T_den = np.array(T.den).ravel()
S = control.minreal(1 - T)
PS = control.minreal(P * S)
PS_den = np.array(PS.den).ravel()
CS = control.minreal(C * S)
CS_den = np.array(CS.den).ravel()
char_poly_tf = control.tf(P.den, 1) * control.tf(C.den, 1) + control.tf(P.num, 1) * control.tf(C.num, 1)
char_poly = np.array(char_poly_tf.num).ravel()
char_poly_roots = np.roots(char_poly)
print(f'The roots of the characteristic polynomial are {char_poly_roots}\n')
print(f'The real part of the roots of the characteristic polynomial are {np.real(char_poly_roots)}\n')
print(f'S = {S}')
print(f'CS = {CS}')
print(f'PS = {PS}')
print(f'T = {T}')
print(f'C = {C}\n')
# %%
# Bode magnitude of P, C, and L
mag_abs, _, w = control.bode(P, w_shared, plot=False)
mag_dB_P = 20 * np.log10(mag_abs)
mag_abs, _, w = control.bode(C, w_shared, plot=False)
mag_dB_C = 20 * np.log10(mag_abs)
mag_abs, _, w = control.bode(L, w_shared, plot=False)
mag_dB_L = 20 * np.log10(mag_abs)
fig, ax = plt.subplots()
# fig.set_size_inches(8.5, 11, forward=True)
ax.set_xlabel(r'$\omega$ (rad/s)')
ax.set_ylabel(r'Magnitude (dB)')
# Magnitude plot (dB).
ax.semilogx(w, mag_dB_P, '-', color='C0', label=r'$|P(j \omega)|$')
ax.semilogx(w, mag_dB_C, '--', color='C1', label=r'$|C(j \omega)|$')
ax.semilogx(w, mag_dB_L, '-.', color='C2', label=r'$|L(j \omega)|$')
ax.semilogx(w_ref_max, gamma_r_dB, '*', color='C6', label=r'desired bandwidth')
ax.legend(loc='best')
fig.tight_layout()
# fig.savefig(path.joinpath('PCL.pdf'))
# %%
# Bode magnitude of S
mag_abs, _, w = control.bode(S, w_shared, plot=False)
mag_dB_S = 20 * np.log10(mag_abs)
fig, ax = plt.subplots()
# fig.set_size_inches(8.5, 11, forward=True) ax.set_xlabel(r'$\omega$ (rad/s)') ax.set_ylabel(r'Magnitude (dB)')
# Magnitude plot (dB).
ax.semilogx(w, mag_dB_S, '-', color='C0', label=r'$|S(j \omega)|$')
ax.semilogx(w_ref_max, gamma_r_dB, '*', color='C6', label=r'desired bandwidth')
ax.legend(loc='best')
fig.tight_layout()
# fig.savefig(path.joinpath('S.pdf'))
# %%
# Bode magnitude of T
mag_abs, _, w = control.bode(T, w_shared, plot=False)
mag_dB_T = 20 * np.log10(mag_abs)
fig, ax = plt.subplots()
# fig.set_size_inches(8.5, 11, forward=True) ax.set_xlabel(r'$\omega$ (rad/s)') ax.set_ylabel(r'Magnitude (dB)')
# Magnitude plot (dB).
ax.semilogx(w, mag_dB_T, '-', color='C0', label=r'$|T(j \omega)|$')
ax.semilogx(w_ref_max, gamma_r_dB, '*', color='C6', label=r'desired bandwidth')
ax.legend(loc='best')
fig.tight_layout()
# fig.savefig(path.joinpath('T.pdf'))
# %%
# Bode magnitude of C * S, which is r to u
mag_abs, _, w = control.bode(CS, w_shared, plot=False)
mag_dB_CS = 20 * np.log10(mag_abs)
fig, ax = plt.subplots()
# fig.set_size_inches(8.5, 11, forward=True)
ax.set_xlabel(r'$\omega$ (rad/s)')
ax.set_ylabel(r'Magnitude (dB)')
# Magnitude plot (dB).
ax.semilogx(w, mag_dB_CS, '-', color='C0', label=r'$|C(j \omega) S(j \omega) |$')
ax.semilogx(w_ref_max, gamma_r_dB, '*', color='C6', label=r'desired bandwidth')
ax.legend(loc='best')
fig.tight_layout()
# fig.savefig(path.joinpath('CS.pdf'))
# %%
# Time-domaine forced response
# Square wave input
#r = 0.1 * signal.square(w_ref_max * t)
r = 0.1 * np.sin(w_ref_max * t)
# Forced response of each system_
_, e_S = control.forced_response(S, t, r)
_, y_T = control.forced_response(T, t, r)
_, u_CS = control.forced_response(CS, t, r)
# Plot forced response
fig, ax = plt.subplots(3, 1)
ax[0].set_ylabel(r'$y(t)$ (units)')
ax[1].set_ylabel(r'$e(t)$ (units)')
ax[2].set_ylabel(r'$u(t)$ (units)')
# Plot data
ax[0].plot(t, r, '--', label='$r(t)$', color='C6')
ax[0].plot(t, y_T, label='$y(t)$', color='C0')
ax[1].plot(t, e_S, label='$e(t)$', color='C1')
ax[2].plot(t, u_CS, label='$u(t)$', color='C2')
for a in np.ravel(ax):
    a.set_xlabel(r'$t$ (s)')
    a.legend(loc='upper right')
fig.tight_layout()

t_T, y_T = control.impulse_response(T, t)

# Plot impulse response
fig, ax = plt.subplots()
ax.set_xlabel(r'$t$ (s)')
ax.set_ylabel(r'$y(t)$ (units)')
ax.plot(t_T, y_T, label='$T(s)$', color='C4')
for a in np.ravel(ax):
    a.set_xlabel(r'$t$ (s)')
    a.legend(loc='upper right')
plt.show()
# fig.savefig('figs/control_square_wave_response.pdf')
# %%
# Plot plt.show()
