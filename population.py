# Реализация класса популяции для симуляции распространения вируса
# Тут находится вся логика эпидемии и перемещения агентов

import numpy as np
from enum import Enum

# Перечисление возможных статусов (не уверен, что это нужно, но звучит умно)
class Status(Enum):
    SUSCEPTIBLE = 0  # восприимчивый (не заражен)
    INFECTED = 1     # заражен
    RECOVERED = 2    # выздоровел (с иммунитетом)
    VACCINATED = 3   # вакцинирован

class Population:
    def __init__(self, size=200, initial_infected=5, infection_rate=0.3, 
                 recovery_time=150, immunity_time=200, interaction_radius=0.03, 
                 movement_speed=0.01, quarantine_enabled=False, quarantine_threshold=30,
                 vaccination_enabled=False, vaccination_start=300, vaccination_rate=3):
        
        # Основные параметры
        self.size = size
        self.infection_rate = infection_rate
        self.recovery_time = recovery_time
        self.immunity_time = immunity_time
        self.interaction_radius = interaction_radius
        
        # Флаги и настройки для особых условий
        self.quarantine_enabled = quarantine_enabled
        self.quarantine_threshold = quarantine_threshold / 100  # переводим проценты в долю
        self.quarantine_active = False
        self.vaccination_enabled = vaccination_enabled
        self.vaccination_start = vaccination_start
        self.vaccination_rate = vaccination_rate
        
        # Инициализация позиций и скоростей (разделяем людей на 4 части чтобы не все в одной куче были)
        self.positions = np.zeros((size, 2))
        for i in range(size):
            quadrant = i % 4
            if quadrant == 0:
                self.positions[i] = np.random.rand(2) * 0.4 + np.array([0.1, 0.1])
            elif quadrant == 1:
                self.positions[i] = np.random.rand(2) * 0.4 + np.array([0.5, 0.1])
            elif quadrant == 2:
                self.positions[i] = np.random.rand(2) * 0.4 + np.array([0.1, 0.5])
            else:
                self.positions[i] = np.random.rand(2) * 0.4 + np.array([0.5, 0.5])
        
        # Изначальные скорости (случайное направление)
        self.velocities = (np.random.rand(size, 2) - 0.5) * movement_speed
        
        # Инициализация статусов и таймеров
        self.status = np.zeros(size, dtype=int)
        self.timers = np.zeros(size, dtype=int)
        
        # Заражение начального числа людей
        self.status[np.random.choice(range(size), initial_infected, replace=False)] = Status.INFECTED.value
        self.timers[self.status == Status.INFECTED.value] = self.recovery_time
        
        # История для графиков (сюда записывается количество людей в каждом статусе на каждом шаге)
        self.history_susceptible = []
        self.history_infected = []
        self.history_recovered = []
        self.history_vaccinated = []
        
        # Счетчик времени
        self.time = 0
        
        # Запоминаем изначальную скорость, чтобы вернуться к ней после карантина
        self.original_movement_speed = movement_speed
        self.current_movement_speed = movement_speed
        
    def update(self):
        """Обновляет состояние популяции на один шаг времени"""
        self.time += 1
        
        # Применяем карантин если нужно (в карантине люди двигаются медленнее)
        infected_percent = np.sum(self.status == Status.INFECTED.value) / self.size
        
        if self.quarantine_enabled:
            if infected_percent >= self.quarantine_threshold and not self.quarantine_active:
                # Вводим карантин
                self.current_movement_speed = self.original_movement_speed * 0.3  # уменьшаем скорость на 70%
                self.quarantine_active = True
                print(f"День {self.time}: Введен карантин (заражено {infected_percent*100:.1f}% населения)")
            
            elif infected_percent < self.quarantine_threshold * 0.5 and self.quarantine_active:
                # Снимаем карантин если заражено меньше половины порогового значения
                self.current_movement_speed = self.original_movement_speed
                self.quarantine_active = False
                print(f"День {self.time}: Карантин снят (заражено {infected_percent*100:.1f}% населения)")
        
        # Обновление позиций
        self.positions += self.velocities
        
        # Отражение от границ
        mask_x = (self.positions[:, 0] <= 0) | (self.positions[:, 0] >= 1)
        mask_y = (self.positions[:, 1] <= 0) | (self.positions[:, 1] >= 1)
        self.velocities[mask_x, 0] *= -1
        self.velocities[mask_y, 1] *= -1
        
        # Применение границ (чтобы точки не вылезали за пределы)
        self.positions = np.clip(self.positions, 0, 1)
        
        # Добавим небольшие случайные изменения в скорости для более естественного движения
        # Использую маленькие значения чтобы движение было плавным
        self.velocities += (np.random.rand(self.size, 2) - 0.5) * 0.002
        
        # Нормализуем скорости, чтобы они не становились слишком большими или маленькими
        speeds = np.linalg.norm(self.velocities, axis=1)
        too_fast = speeds > self.current_movement_speed * 1.5
        if np.any(too_fast):
            scale = (self.current_movement_speed * 1.5) / speeds[too_fast]
            self.velocities[too_fast] *= scale[:, np.newaxis]
        
        # Обработка инфекций
        infected = np.where(self.status == Status.INFECTED.value)[0]
        susceptible = np.where(self.status == Status.SUSCEPTIBLE.value)[0]
        
        if len(infected) > 0 and len(susceptible) > 0:
            # Вычисление заражений (не оптимальный код, но работает)
            for s_idx in susceptible:
                # Проверяем расстояние до каждого инфицированного
                for i_idx in infected:
                    distance = np.linalg.norm(self.positions[s_idx] - self.positions[i_idx])
                    
                    # Если расстояние меньше радиуса взаимодействия, есть шанс заражения
                    if distance < self.interaction_radius:
                        # тут тупая проверка, но поработает для моделирования
                        if np.random.rand() < self.infection_rate:
                            self.status[s_idx] = Status.INFECTED.value
                            self.timers[s_idx] = self.recovery_time
                            break  # переходим к следующему восприимчивому
        
        # Обновление таймеров инфицированных
        infected_mask = self.status == Status.INFECTED.value
        self.timers[infected_mask] -= 1
        
        # Выздоровление
        recovery_mask = (self.status == Status.INFECTED.value) & (self.timers <= 0)
        self.status[recovery_mask] = Status.RECOVERED.value
        self.timers[recovery_mask] = self.immunity_time
        
        # Потеря иммунитета
        immunity_loss_mask = (self.status == Status.RECOVERED.value) & (self.timers > 0)
        self.timers[immunity_loss_mask] -= 1
        
        no_immunity_mask = (self.status == Status.RECOVERED.value) & (self.timers <= 0)
        self.status[no_immunity_mask] = Status.SUSCEPTIBLE.value
        
        # Вакцинация (если включена и наступило время)
        if self.vaccination_enabled and self.time >= self.vaccination_start:
            # Находим людей, которых можно вакцинировать (только восприимчивые)
            potential_vaccinated = np.where(self.status == Status.SUSCEPTIBLE.value)[0]
            
            if len(potential_vaccinated) > 0:
                # Вакцинируем определенное количество людей
                to_vaccinate = min(self.vaccination_rate, len(potential_vaccinated))
                
                if to_vaccinate > 0:
                    vaccinated_idx = np.random.choice(potential_vaccinated, to_vaccinate, replace=False)
                    self.status[vaccinated_idx] = Status.VACCINATED.value
                    
                    # если начинаем вакцинацию, выводим сообщение
                    if self.time == self.vaccination_start:
                        print(f"День {self.time}: Началась вакцинация населения")
        
        # Сохранение истории для графиков
        self.history_susceptible.append(np.sum(self.status == Status.SUSCEPTIBLE.value))
        self.history_infected.append(np.sum(self.status == Status.INFECTED.value))
        self.history_recovered.append(np.sum(self.status == Status.RECOVERED.value))
        self.history_vaccinated.append(np.sum(self.status == Status.VACCINATED.value))
        
        return self.status.copy()