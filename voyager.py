import krpc
import time
import math

# Подключение к KSP
connection = krpc.connect(name='OrbitInsertion')
vessel = connection.space_center.active_vessel
control = vessel.control
flight = vessel.flight(vessel.orbit.body.reference_frame)

print("Старт...")

# Включение систем
control.sas = True
control.rcs = True
control.throttle = 1.0

# Запуск первых ступеней
control.activate_next_stage()
control.activate_next_stage()

# Вертикальный подъём до 10 км
vessel.auto_pilot.engage()
vessel.auto_pilot.target_pitch_and_heading(90, 90)
vessel.auto_pilot.wait()

while vessel.flight().mean_altitude < 10000:
    time.sleep(0.1)

print("10 км: начинаем гравитационный поворот")

# Гравитационный поворот (10 000–40 000 м)
turn_start_alt = 10000
turn_end_alt = 40000
target_pitch = 0

while vessel.flight().mean_altitude < turn_end_alt:
    alt = vessel.flight().mean_altitude
    ratio = (alt - turn_start_alt) / (turn_end_alt - turn_start_alt)
    current_pitch = max(target_pitch, 90 - 90 * ratio)
    vessel.auto_pilot.target_pitch_and_heading(current_pitch, 90)
    time.sleep(0.1)

print("Гравитационный поворот завершён. Держим курс 0°.")
vessel.auto_pilot.target_pitch_and_heading(0, 90)

# Подъём до 45 км и отделение ускорителей
while vessel.flight().mean_altitude < 45000:
    time.sleep(0.1)

print("45 км: контроль топлива ускорителей")

while True:
    solid_fuel = vessel.resources.amount('SolidFuel')
    if solid_fuel <= 0.1:
        print("Топливо ускорителей исчерпано. Отделяем ступень.")
        control.throttle = 0.0
        time.sleep(0.5)
        control.activate_next_stage()
        time.sleep(1)
        print("Включаем жидкостный двигатель.")
        control.throttle = 1.0
        break
    time.sleep(1)

print("Переход на жидкостный двигатель. Начало разгона.")

# Параметры орбиты
target_apogee = 80000      # 80 км
target_periapsis = 80000     # 80 км
cutoff_apogee = 75000       # Отключаем при 75 км (запас 5 км)

# Фаза разгона (45 000–70 000 м)
while vessel.flight().mean_altitude < 70000:
    alt = vessel.flight().mean_altitude
    apogee = vessel.orbit.apoapsis_altitude

    # Плавное снижение тангажа: 0° → −15°
    pitch_target = -15 * ((alt - 45000) / 25000)
    vessel.auto_pilot.target_pitch_and_heading(pitch_target, 90)

    # Регулировка тяги по апогею
    if apogee < cutoff_apogee:
        control.throttle = 1.0  # Полный газ
    elif apogee < target_apogee:
        control.throttle = 0.7  # Снижаем до 70%
    else:
        control.throttle = 0.0  # Отключаем
        print(f"Апогей достиг {int(apogee)} м. Отключаем двигатель.")
        break

    time.sleep(0.1)

# Ожидание подхода к апогею для коррекции
print("Ожидаем апогей для круговой коррекции...")
while True:
    time_to_apoapsis = vessel.orbit.time_to_apoapsis
    if time_to_apoapsis < 10:
        break
    time.sleep(1)

print("В апогее. Начинаем коррекцию перигея.")

# Коррекция перигея в апогее
control.throttle = 1.0
vessel.auto_pilot.target_pitch_and_heading(0, 90)  # Горизонтально по движению

while vessel.orbit.periapsis_altitude < target_periapsis:
    # Если перигей уже близок, снижаем тягу
    if vessel.orbit.periapsis_altitude > target_periapsis - 1000:
        control.throttle = 0.3
    time.sleep(0.1)

print("Перигей выровнен. Орбита круговая!")
control.throttle = 0.0
control.throttle = 0.0

vessel.auto_pilot.engage()

print(f"Выход на орбиту завершён. ")
ref_frame = vessel.orbit.body.reference_frame

vessel.auto_pilot.reference_frame = ref_frame

# Получаем вектор скорости в системе отсчёта планеты
velocity_vec = vessel.flight(ref_frame).velocity
vessel.auto_pilot.target_direction = velocity_vec
vessel.auto_pilot.wait()
