import math
import matplotlib.pyplot as plt
import pandas as pd


t1 = 97         # Время завершения работы 1 ступени (в секундах)
t2 = 380        # Время включения двигателей 2 ступени (в секундах)
t3 = 410        # Время выхода на орбиту (в секундах)
t4 = 420        # Время завершения программы (в секундах)
delta_time = 1  # Шаг изменения времени (1 секунда)

g0 = 9.81       # Ускорение свободного падения на поверхности Земли (м/c^2)
P0 = 101325     # Давление атмосферы Земли на уровне моря (Па)
p0 = 1.225      # Начальная плотность атмосферы (кг/м^3)
m0 = 176 * 10 ** 3  # Масса ракеты на момент старта (кг)

r_kerbin = 600000   # Радиус Кербина (м)

F1_min = 2443.67 * 10 ** 3      # Сила тяги 1 ступени на момент старта (Н)
F1_max = 3100 * 10 ** 3         # Максимальная сила тяги 2 ступени, достигаемая в вакууме (Н)
F2 = 750 * 10 ** 3              # Сила тяги 1 ступени в вакууме (Н)
I1 = 205                        # Удельный импульс 1 ступени (с)
I2 = 310                        # Удельный импульс 2 ступени (с)


pitch = 90                  # Тангаж на момент старта (градусы)
Cx = 0.5                    # Коэффициент лобового сопротивления
d = 3.05                    # Диаметр ракеты (м)
S = math.pi * d ** 2 / 4    # Площадь поперечного сечения ракеты (м^2)


# Здесь будут храниться посчитанные данные
data = {
    'time': [],
    'speed': [],
    'altitude': [],
    'mass': [],
    'speed' : []
}


# Выставляются начальные данные:
time = 0    # Время с момента старта
m = m0      # Масса ракеты в данную секунду
F1 = F1_min # Силя тяги в данную секунду
V = 0       # Скорость ракеты относительно поверхности земли в данную секунду
h = 0       # Высота над поверхностью земли в данную секунду

# Работают ускорители
while time <= t1:
    time += delta_time
    F1 += (F1_max - F1_min)/t1                  # Сила тяги меняется линейно (допущение)
    g = g0 * (r_kerbin / (r_kerbin + h)) ** 2   # Формула ускорения свободного падения
    p = p0 * math.exp(-p0 * g * h / P0)         # Формула плотности атмосферы
    m -= delta_time * F1 / (I1 * g0)            # По формуле изменения массы ракеты
    pitch =  math.radians(90 - 90*(time/t4))    # Тангаж меняет линейно (допущение)
    V += I1*g*math.log(m/(m - delta_time * F1 / (I1 * g0))) - (Cx*S/2) * (p*(V**2)/m) - g   # Формула Циолковского и гравитационные потери
    h += math.sin(pitch) * V * delta_time       # Меняем высоту в зависимости от вертикальной составляющей скорости в данную секунду

    data['time'].append(time)
    data['mass'].append(m)
    data['altitude'].append(h)
    data['speed'].append(V)

m = 23000   # Масса ракеты после сброса ускорителей
# Двигатели выключены
while time < t2:
    time += delta_time
    g = g0 * (r_kerbin / (r_kerbin + h)) ** 2   # Формула ускорения свободного падения
    pitch = math.radians(90 - 90*(time/t4))     # Тангаж меняет линейно (допущение)
    V = ((math.cos(pitch) * V) ** 2 + (math.sin(pitch) * V - g*delta_time/2)** 2) ** 0.5    # Теорема Пифагора для скорости (меняется только вертикальная составляющая)
    h += math.sin(pitch) * V * delta_time / 2   # Меняем высоту в зависимости от вертикальной составляющей скорости в данную секунду
    
    data['time'].append(time)
    data['altitude'].append(h)
    data['mass'].append(m)
    data['speed'].append(V)

# Двигатели включены
while time <= t3:
    time += delta_time
    pitch = math.radians(90 - 90*(time/t4))     # Тангаж меняет линейно (допущение)
    g = g0 * (r_kerbin / (r_kerbin + h)) ** 2   # Формула ускорения свободного падения
    m -= delta_time * F2 / (I2 * g0)            # По формуле изменения массы ракеты
    V += I2*g*math.log(m/(m - delta_time * F2 / (I2 * g0))) - g     # Формула Циолковского и гравитационные потери
    h += math.sin(pitch) * V                    # Меняем высоту в зависимости от вертикальной составляющей скорости в данную секунду

    data['time'].append(time)
    data['altitude'].append(h)
    data['mass'].append(m)
    data['speed'].append(V)


# Часть, когда ракета уже на орбите
while time <= t4:
    time += 1
    data['time'].append(time)
    data['altitude'].append(h)
    data['mass'].append(m)
    data['speed'].append(V)


# Загрузка данных из KSP
ksp_data = pd.read_csv('all.csv')

ksp_data = {
    'time' : ksp_data['Time'][:t4 + 1],                             # Время (t)
    'speed' : ksp_data['Surface Speed (m/s)'][:t4 + 1],             # Скорость (v(t))
    'mass' : ksp_data['Mass (t)'][:t4 + 1],                         # Масса (m(t))
    'altitude' : ksp_data['Altitude from Terrain (m)'][:t4 + 1]     # Высота (h)
}

for i in range(t4 + 1):
    ksp_data['mass'][i] = 1000*ksp_data['mass'][i] # Перевод из тонн в килограммы




# Построение графиков
fig, axes = plt.subplots(3, 1, figsize=(10, 10))

#1-ый график: скорость от времени
axes[0].plot(data['time'], ksp_data['speed'], label='KSP', color='green', linewidth=2)
axes[0].plot(data['time'], data['speed'], label='Модель', color='blue', linewidth=2)
axes[0].set_xlabel('Время (с)', fontsize=12)
axes[0].set_ylabel('Скорость (м/с)', fontsize=12)
axes[0].set_title('Зависимость скорости от времени', fontsize=14, fontweight='bold')
axes[0].grid(True, alpha=0.3)
axes[0].legend(loc='best')


#2-ой график: высота от времени
axes[1].plot(data['time'], ksp_data['altitude'], label='KSP', color='green', linewidth=2)
axes[1].plot(data['time'], data['altitude'], label='Модель', color='blue', linewidth=2)
axes[1].set_xlabel('Время (с)', fontsize=12)
axes[1].set_ylabel('Высота (м)', fontsize=12)
axes[1].set_title('Зависимость высоты от времени', fontsize=14, fontweight='bold')
axes[1].grid(True, alpha=0.3)
axes[1].legend(loc='best')


#3-ий график: масса от времени
axes[2].plot(data['time'], ksp_data['mass'], label='KSP', color='green', linewidth=2)
axes[2].plot(data['time'], data['mass'], label='Модель', color='blue', linewidth=2)
axes[2].set_xlabel('Время (с)', fontsize=12)
axes[2].set_ylabel('Масса (м)', fontsize=12)
axes[2].set_title('Зависимость массы от времени', fontsize=14, fontweight='bold')
axes[2].grid(True, alpha=0.3)
axes[2].legend(loc='best')

plt.tight_layout()
plt.show()
