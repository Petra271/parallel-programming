import numpy as np
import matplotlib.pyplot as plt

m = 0.200  # g
Ek0 = 20.0  # J
alfa_st = 45.0
alfa = np.radians(alfa_st)
g = 9.81

v0 = np.sqrt(2 * Ek0 / m)

print("pocetna brzina je {:.3g} m/s".format(v0))

y = (v0**2 * (np.sin(alfa)) ** 2) / (2 * g)

print("Maksimalna visina je: {:.3g} [m]".format(y))

Ep_max = m * (v0 * np.sin(alfa)) ** 2 / 2

# vy = 0
# vx = v0

Ek_max = m * (v0 * np.cos(alfa)) ** 2 / 2

print("Potencijalna energija u najvišoj točki je: {:.1f} [J]".format(Ep_max))
print("Kinetička energija u najvišoj točki je: {:.1f} [J]".format(Ek_max))


tuk = 2 * v0 * np.sin(alfa) / g
t = np.linspace(0, tuk, 100)
y1 = v0 * t * np.sin(alfa) - 1 / 2 * g * t**2
# y1 = np.linspace(0, y, 50)
# y2 = np.linspace(y, 0, 50)
Ep = m * g * y1

Euk = (Ep_max + Ek_max) * np.ones(100)
Ek = Euk - Ep
plt.plot(t, Ep, "b", t, Ek, "r", t, Euk, "g")
plt.legend(["Ep", "Ek", "Euk"])
plt.xlabel("vrijeme / s")
plt.ylabel("energija / J")
plt.show()
