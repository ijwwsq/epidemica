# Основной файл для запуска симуляции

import numpy as np
import matplotlib.pyplot as plt
import time
from population import Population
from visualization import SimulationVisualizer

# Начинаем отсчет времени выполнения (нужно для отчета)
start_time = time.time()

# Параметры симуляции (менял сто раз, эти вроде работают)
POPULATION_SIZE = 200        # чел.
INITIAL_INFECTED = 3         # чел.
INFECTION_RATE = 0.4         # вероятность заражения при контакте
RECOVERY_TIME = 150          # время болезни (шагов)
IMMUNITY_TIME = 200          # длительность иммунитета (шагов)
INTERACTION_RADIUS = 0.025   # радиус взаимодействия
MOVEMENT_SPEED = 0.01        # скорость перемещения
QUARANTINE_ENABLED = True    # включить карантин
QUARANTINE_THRESHOLD = 30    # % зараженных, при котором вводится карантин
VACCINATION_ENABLED = True   # включить вакцинацию
VACCINATION_START = 300      # когда начинается вакцинация (шаг)
VACCINATION_RATE = 5         # сколько человек вакцинируется за шаг

FRAMES = 900                # длительность симуляции
INTERVAL = 20               # интервал между кадрами (мс)

# Обработчик ошибки если что-то пойдет не так
try:
    # выводим инфу о параметрах - пригодится для отчета
    print("=== ЗАПУСК СИМУЛЯЦИИ РАСПРОСТРАНЕНИЯ ВИРУСА ===")
    print(f"Размер популяции: {POPULATION_SIZE}")
    print(f"Начальное число зараженных: {INITIAL_INFECTED}")
    print(f"Вероятность заражения: {INFECTION_RATE}")
    print(f"Карантин: {'Включен' if QUARANTINE_ENABLED else 'Выключен'}")
    print(f"Вакцинация: {'Включена' if VACCINATION_ENABLED else 'Выключена'}")
    
    # Создаем объекты для симуляции
    population = Population(
        size=POPULATION_SIZE,
        initial_infected=INITIAL_INFECTED,
        infection_rate=INFECTION_RATE,
        recovery_time=RECOVERY_TIME,
        immunity_time=IMMUNITY_TIME,
        interaction_radius=INTERACTION_RADIUS,
        movement_speed=MOVEMENT_SPEED,
        quarantine_enabled=QUARANTINE_ENABLED,
        quarantine_threshold=QUARANTINE_THRESHOLD,
        vaccination_enabled=VACCINATION_ENABLED,
        vaccination_start=VACCINATION_START,
        vaccination_rate=VACCINATION_RATE
    )
    
    # Создаем визуализатор
    visualizer = SimulationVisualizer(population, frames=FRAMES, interval=INTERVAL)
    
    # Запускаем симуляцию
    visualizer.run()
    
    # Выводим итоговую статистику для отчета
    total_time = time.time() - start_time
    print(f"\n==== РЕЗУЛЬТАТЫ СИМУЛЯЦИИ ====")
    print(f"Продолжительность: {population.time} шагов")
    print(f"Максимум зараженных: {max(population.history_infected)} человек ({max(population.history_infected)/POPULATION_SIZE*100:.1f}%)")
    print(f"Время выполнения: {total_time:.2f} сек.")
    
    # Выводим график в конце
    visualizer.show_final_results()
    
except Exception as e:
    # В последний момент спохватился добавить обработку ошибок
    print(f"Ошибка: {e}")
    print("Что-то пошло не так при выполнении симуляции!")