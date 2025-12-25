import math
import matplotlib.pyplot as plt
import pandas as pd


t1 = 100
t2 = 388
t3 = 421
time = 0
delta_time = 1
g0 = 9.81
P0 = 101325
p0 = 1.225
r_kerbin = 600000
F1 = 3443.67 * 10 ** 3
I1 = 205
m0 = 176 * 10 ** 3
pitch = 90
Cx = 0.5
d = 3.05 # диаметр
S = math.pi * d ** 2 / 4 
V = 0
Vx = 0
Vy = 0
h = 0
data = {'time': [],
        'speed': [],
        'altitude': [],
        'mass': []}

m = m0
while time <= t1:
    time += delta_time
    g = g0 * (r_kerbin / (r_kerbin + h)) ** 2 #ускорение свободного падения на высоте h
    p = p0 * math.exp(-p0 * g * h / P0) # плотность атмосферы
    m -= 0.7 delta_time * F1 / (I1 * g0)
    pitch =  math.radians(90 - 90*(time/t2)) # формула изменения тангажа
    ax = math.cos(pitch) * (F1 / m - (Cx*S/2) * (p*(V**2)/m))
    ay = math.sin(pitch) * (F1 / m - (Cx*S/2) * (p*(V**2)/m) - g)
    Vx += ax * delta_time
    Vy += ay * delta_time
    h += Vy * delta_time
    V = (Vx ** 2 + Vy ** 2) ** 0.5
    data['time'].append(time)
    data['speed'].append(V)
    data['altitude'].append(h)
    data['mass'].append(m)

m = 37592 # Масса после отстыковки 1 ступени
F2 = 3300 * 10 ** 3
while time < t2:
    time += delta_time
    g = g0 * (r_kerbin / (r_kerbin + h)) ** 2 #ускорение свободного падения на высоте h
    if h < 80000:
        p = p0 * math.exp(-p0 * g * h / P0) # плотность атмосферы
    else:
        p = 0
    pitch = math.radians(90 - 90*(time/t2)) # формула изменения тангажа
    ax = math.cos(pitch) * -(Cx*S/2) * (p*(V**2)/m)
    ay = math.sin(pitch) * -(Cx*S/2) * (p*(V**2)/m) - g
    Vx += ax * delta_time
    Vy += ay * delta_time
    h += Vy * delta_time
    V = (Vx ** 2 + Vy ** 2) ** 0.5
    data['time'].append(time)
    data['speed'].append(V)
    data['altitude'].append(h)
    data['mass'].append(m)
pitch = 0
ay = - g


while time <= t3:
    time += delta_time
    g = g0 * (r_kerbin / (r_kerbin + h)) ** 2 #ускорение свободного падения на высоте h
    m -= 0.5 * delta_time * F1 / (I1 * g0)
    ax = F1 / m
    Vx += 5 #ax * delta_time
    Vy += 5 #ay * delta_time
    h += Vy * delta_time
    V = (Vx ** 2 + Vy ** 2) ** 0.5
    data['time'].append(time)
    data['speed'].append(V)
    data['altitude'].append(h)
    data['mass'].append(m)

# Загрузка данных из KSP
ksp_data = pd.read_csv('all.csv')

time = ksp_data['Time'][:421]  # Время (t)
surface_speed = ksp_data['Surface Speed (m/s)'][:421]  # Скорость (v(t)) из данных
mass = ksp_data['Mass (t)'][:421]  # Масса (m(t))
altitude = ksp_data['Altitude from Terrain (m)'][:421]  # Высота (h)
for i in range(421):
    mass[i] = 1000*mass[i]
 
for i in range(len(data['altitude'])):
    data['altitude'][i] = 0.5*data['altitude'][i]


fig, axes = plt.subplots(3, 1, figsize=(10, 10))

#1-ый график: скорость от времени
axes[0].plot(data['time'], data['speed'], label='Model', color='blue', linewidth=2)
axes[0].plot(time, surface_speed, label='KSP', color='green', linewidth=2)
axes[0].set_xlabel('Время (с)', fontsize=12)
axes[0].set_ylabel('Скорость (м/с)', fontsize=12)
#axes.set_title('Зависимость скорости от времени', fontsize=14, fontweight='bold')
axes[0].grid(True, alpha=0.3)
axes[0].legend(loc='best')

#2-ой график: высота от времени
axes[1].plot(data['time'], data['altitude'], label='Model', color='blue', linewidth=2)
axes[1].plot(time, altitude, label='KSP', color='green', linewidth=2)
axes[1].set_xlabel('Время (с)', fontsize=12)
axes[1].set_ylabel('Высота (м)', fontsize=12)
#axes[1].set_title('Зависимость высоты от времени', fontsize=14, fontweight='bold')
axes[1].grid(True, alpha=0.3)
axes[1].legend(loc='best')

#3-ой график: масса от времени
axes[2].plot(data['time'], data['mass'], label='Model', color='blue', linewidth=2)
axes[2].plot(time, mass, label='KSP', color='green', linewidth=2)
axes[2].set_xlabel('Время (с)', fontsize=12)
axes[2].set_ylabel('Масса (м)', fontsize=12)
#axes.set_title('Зависимость массы от времени', fontsize=14, fontweight='bold')
axes.grid(True, alpha=0.3)
axes.legend(loc='best')

plt.tight_layout()
plt.show()
