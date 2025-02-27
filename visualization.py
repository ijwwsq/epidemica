# Реализация визуализации для симуляции распространения вируса

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import ListedColormap
import matplotlib.patches as mpatches
from enum import Enum

# Для совместимости с population.py
class Status(Enum):
    SUSCEPTIBLE = 0  # восприимчивый (не заражен)
    INFECTED = 1     # заражен
    RECOVERED = 2    # выздоровел (с иммунитетом)
    VACCINATED = 3   # вакцинирован

class SimulationVisualizer:
    def __init__(self, population, frames=1000, interval=20):
        self.population = population
        self.frames = frames
        self.interval = interval
        
        # Настраиваем фигуру и оси
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Настраиваем цветовую схему для точек
        # [здоровый, инфицированный, выздоровевший, вакцинированный]
        self.colors = ['#3498db', '#e74c3c', '#2ecc71', '#9b59b6']
        self.cmap = ListedColormap(self.colors)
        
        # Инициализация точек
        self.scatter = self.ax1.scatter(
            [], [], c=[], cmap=self.cmap, 
            vmin=0, vmax=3, s=30, alpha=0.7
        )
        
        # Настройка правой половины с графиками
        self.line_susceptible, = self.ax2.plot([], [], color=self.colors[0], label='Восприимчивые')
        self.line_infected, = self.ax2.plot([], [], color=self.colors[1], label='Инфицированные')
        self.line_recovered, = self.ax2.plot([], [], color=self.colors[2], label='Выздоровевшие')
        self.line_vaccinated, = self.ax2.plot([], [], color=self.colors[3], label='Вакцинированные')
        
        # Добавляем текст для показа текущей статистики
        self.stats_text = self.ax1.text(
            0.05, 0.05, '', transform=self.ax1.transAxes,
            bbox=dict(facecolor='white', alpha=0.7)
        )
        
        # Настраиваем границы графиков
        self.setup_axes()
        
    def setup_axes(self):
        """Настраиваем параметры осей и графиков"""
        # Настройка графика симуляции
        self.ax1.set_xlim(0, 1)
        self.ax1.set_ylim(0, 1)
        self.ax1.set_title('Симуляция распространения вируса')
        self.ax1.set_xticks([])
        self.ax1.set_yticks([])
        
        # Легенда для симуляции
        susceptible_patch = mpatches.Patch(color=self.colors[0], label='Восприимчивые')
        infected_patch = mpatches.Patch(color=self.colors[1], label='Инфицированные')
        recovered_patch = mpatches.Patch(color=self.colors[2], label='Выздоровевшие')
        vaccinated_patch = mpatches.Patch(color=self.colors[3], label='Вакцинированные')
        
        self.ax1.legend(
            handles=[susceptible_patch, infected_patch, recovered_patch, vaccinated_patch],
            loc='upper right', fontsize=8
        )
        
        # Настройка графика динамики
        self.ax2.set_xlim(0, self.frames)
        self.ax2.set_ylim(0, self.population.size)
        self.ax2.set_xlabel('Время (дни)')
        self.ax2.set_ylabel('Количество людей')
        self.ax2.set_title('Динамика распространения вируса')
        self.ax2.grid(True, alpha=0.3)
        self.ax2.legend(loc='upper right')
    
    def init_animation(self):
        """Инициализация анимации"""
        self.scatter.set_offsets(self.population.positions)
        self.scatter.set_array(self.population.status)
        
        self.line_susceptible.set_data([], [])
        self.line_infected.set_data([], [])
        self.line_recovered.set_data([], [])
        self.line_vaccinated.set_data([], [])
        
        self.stats_text.set_text('')
        
        return (self.scatter, self.line_susceptible, self.line_infected, 
                self.line_recovered, self.line_vaccinated, self.stats_text)
    
    def update_frame(self, frame):
        """Обновление кадра анимации"""
        # Обновление модели
        self.population.update()
        
        # Обновление положений и цветов точек
        self.scatter.set_offsets(self.population.positions)
        self.scatter.set_array(self.population.status)
        
        # Обновление линий на графике истории
        t = range(len(self.population.history_susceptible))
        self.line_susceptible.set_data(t, self.population.history_susceptible)
        self.line_infected.set_data(t, self.population.history_infected)
        self.line_recovered.set_data(t, self.population.history_recovered)
        self.line_vaccinated.set_data(t, self.population.history_vaccinated)
        
        # Обновление статистики
        s_count = self.population.history_susceptible[-1]
        i_count = self.population.history_infected[-1]
        r_count = self.population.history_recovered[-1]
        v_count = self.population.history_vaccinated[-1]
        
        stats = f'День: {self.population.time}\n'
        stats += f'Восприимчивые: {s_count} ({s_count/self.population.size*100:.1f}%)\n'
        stats += f'Инфицированные: {i_count} ({i_count/self.population.size*100:.1f}%)\n'
        stats += f'Выздоровевшие: {r_count} ({r_count/self.population.size*100:.1f}%)\n'
        stats += f'Вакцинированные: {v_count} ({v_count/self.population.size*100:.1f}%)'
        
        if self.population.quarantine_active:
            stats += '\n[КАРАНТИН ДЕЙСТВУЕТ]'
            
        self.stats_text.set_text(stats)
        
        # Автомасштабирование графика истории
        if frame > 0 and frame % 100 == 0:
            self.ax2.set_xlim(0, min(frame + 100, self.frames))
        
        return (self.scatter, self.line_susceptible, self.line_infected,
                self.line_recovered, self.line_vaccinated, self.stats_text)
    
    def run(self):
        """Запускает анимацию симуляции"""
        self.animation = animation.FuncAnimation(
            self.fig, self.update_frame, frames=range(self.frames),
            init_func=self.init_animation, blit=True, interval=self.interval
        )
        
        # Параметры для сохранения (на всякий случай)
        # self.animation.save('simulation.gif', writer='pillow', fps=20)
        
        plt.tight_layout()
        plt.show()
    
    def show_final_results(self):
        """Показывает итоговый график результатов"""
        plt.figure(figsize=(12, 7))
        
        # Данные для графика
        t = range(len(self.population.history_susceptible))
        
        # Строим графики для разных групп
        plt.plot(t, self.population.history_susceptible, 
                 color=self.colors[0], label='Восприимчивые', linewidth=2)
        plt.plot(t, self.population.history_infected, 
                 color=self.colors[1], label='Инфицированные', linewidth=2)
        plt.plot(t, self.population.history_recovered, 
                 color=self.colors[2], label='Выздоровевшие', linewidth=2)
        plt.plot(t, self.population.history_vaccinated, 
                 color=self.colors[3], label='Вакцинированные', linewidth=2)
        
        # Добавляем вертикальные линии для важных событий
        if self.population.vaccination_enabled:
            plt.axvline(x=self.population.vaccination_start, color='purple', linestyle='--', alpha=0.7)
            plt.text(self.population.vaccination_start + 5, self.population.size * 0.9, 
                     'Начало вакцинации', rotation=90, alpha=0.7)
        
        # Находим первый момент введения карантина
        quarantine_starts = []
        in_quarantine = False
        for i in range(1, len(t)):
            infected_percent = self.population.history_infected[i] / self.population.size
            threshold = self.population.quarantine_threshold
            
            if infected_percent >= threshold and not in_quarantine and self.population.quarantine_enabled:
                quarantine_starts.append(i)
                in_quarantine = True
            elif infected_percent < threshold * 0.5 and in_quarantine:
                in_quarantine = False
        
        # Рисуем линии карантина
        for q_start in quarantine_starts[:1]:  # показываем только первый карантин
            plt.axvline(x=q_start, color='red', linestyle='--', alpha=0.7)
            plt.text(q_start + 5, self.population.size * 0.95, 
                     'Введение карантина', rotation=90, alpha=0.7)
        
        # Добавляем аннотации с пиковыми значениями
        max_infected = max(self.population.history_infected)
        max_infected_idx = self.population.history_infected.index(max_infected)
        
        plt.annotate(f'Пик инфекции: {max_infected} чел. ({max_infected/self.population.size*100:.1f}%)',
                    xy=(max_infected_idx, max_infected),
                    xytext=(max_infected_idx+30, max_infected+20),
                    arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=5),
                    fontsize=9)
        
        # Настраиваем оси и заголовок
        plt.xlabel('Время (дни)')
        plt.ylabel('Количество людей')
        plt.title('Итоговая динамика распространения вируса')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Добавим инфу про параметры симуляции
        model_info = (
            f"Население: {self.population.size} чел.\n"
            f"Зараженность: {self.population.infection_rate}\n"
            f"Длительность болезни: {self.population.recovery_time} дней\n"
            f"Карантин: {'Вкл' if self.population.quarantine_enabled else 'Выкл'}\n"
            f"Вакцинация: {'Вкл' if self.population.vaccination_enabled else 'Выкл'}"
        )
        
        plt.figtext(0.02, 0.02, model_info, fontsize=8, 
                   bbox=dict(facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        plt.show()