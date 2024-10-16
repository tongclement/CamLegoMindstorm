#!/usr/bin/env python3

import time
import threading
import csv
from collections import deque

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.graph import Graph, MeshLinePlot  # Correct import
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.properties import NumericProperty

# Assuming you still need matplotlib for other purposes
import matplotlib.pyplot as plt
from cued_ia_lego import *  # Ensure this library is correctly set up

# Constants
SMOOTHING_FACTOR = 0.05
DATA_DURATION = 60  # seconds to run the data collection

class MotorController(BoxLayout):
    target_speed = NumericProperty(100)  # Default target speed

    def __init__(self, **kwargs):
        super(MotorController, self).__init__(**kwargs)
        self.orientation = 'vertical'

        # Initialize Motors and Brick
        try:
            self.brick = NXTBrick()
        except Exception as e:
            print(f"Failed to connect to NXT Brick: {e}")
            exit()

        # Set up rotor motor
        self.motor_rotor = Motor(self.brick, PORT_A, power=self.target_speed, speedreg=False, smoothstart=True, brake=False)
        self.motor_rotor.reset_position()

        # Set up pitch motor
        self.motor_pitch = Motor(self.brick, PORT_B, power=40, speedreg=True, smoothstart=True, brake=True)
        self.motor_pitch.reset_position()
        self.motor_pitch.turn_to(0)

        self.motor_rotor.run()
        self.motor_armed = True

        # Data storage
        self.times = deque(maxlen=1000)  # Store up to 1000 data points
        self.position_readings = deque(maxlen=1000)
        self.speed_readings = deque(maxlen=1000)

        # Set up Graph
        self.graph = Graph(
            xlabel='Time (s)', ylabel='Motor Speed',
            x_ticks_major=10, y_ticks_major=10,
            y_grid_label=True, x_grid_label=True,
            padding=5, x_grid=True, y_grid=True, xmin=0, xmax=60, ymin=0, ymax=200
        )

        self.plot = MeshLinePlot(color=[0, 1, 0, 1])
        self.graph.add_plot(self.plot)

        self.add_widget(self.graph)

        # Set up Buttons
        button_layout = BoxLayout(size_hint_y=0.2)

        self.btn_increase = Button(text='Increase Speed')
        self.btn_decrease = Button(text='Decrease Speed')
        self.btn_stop = Button(text='Stop Motor')

        self.btn_increase.bind(on_press=self.increase_speed)
        self.btn_decrease.bind(on_press=self.decrease_speed)
        self.btn_stop.bind(on_press=self.stop_motor)

        button_layout.add_widget(self.btn_increase)
        button_layout.add_widget(self.btn_decrease)
        button_layout.add_widget(self.btn_stop)

        self.add_widget(button_layout)

        # Start Data Collection Thread
        self.running = True
        self.start_time = time.perf_counter()
        self.data_thread = threading.Thread(target=self.collect_data)
        self.data_thread.start()

        # Schedule Graph Update
        Clock.schedule_interval(self.update_graph, 1.0 / 30.0)  # 30 FPS

    def collect_data(self):
        t_start = self.start_time
        while self.running and (time.perf_counter() - t_start) < DATA_DURATION:
            current_time = time.perf_counter() - t_start
            try:
                position = self.motor_rotor.get_position()
            except Exception as e:
                print(f"Error reading motor position: {e}")
                position = 0

            self.times.append(current_time)
            self.position_readings.append(position)

            # Calculate motor speed (difference over time)
            if len(self.position_readings) > 1:
                d_position = self.position_readings[-1] - self.position_readings[-2]
                d_time = self.times[-1] - self.times[-2]
                speed = d_position / d_time if d_time > 0 else 0
            else:
                speed = 0

            # Apply smoothing (one-sided moving average) - what this smoothing factor does is the weighting assigned to the current motor speed value (5% weight on the new raw value, 95% previous smoothed average)
            if self.speed_readings:
                smoothed_speed = (1 - SMOOTHING_FACTOR) * self.speed_readings[-1] + SMOOTHING_FACTOR * speed
            else:
                smoothed_speed = speed

            self.speed_readings.append(smoothed_speed)

            # Update target speed if needed
            # For example, you can implement pitch adjustments here

            time.sleep(0.1)  # Adjust the sampling rate as needed

        self.stop_motor()

    def update_graph(self, dt):
        if self.times and self.speed_readings:
            # Shift the x-axis
            current_time = self.times[-1]
            self.graph.xmax = max(60, current_time + 10)
            self.graph.xmin = max(0, current_time - 60)

            self.plot.points = list(zip(self.times, self.speed_readings))

    def increase_speed(self, instance):
        self.target_speed += 10
        if self.target_speed > 200:
            self.target_speed = 200  # Maximum speed limit
        self.motor_rotor.set_power(self.target_speed)
        print(f"Target speed increased to {self.target_speed}")

    def decrease_speed(self, instance):
        self.target_speed -= 10
        if self.target_speed < 0:
            self.target_speed = 0  # Minimum speed limit
        self.motor_rotor.set_power(self.target_speed)
        print(f"Target speed decreased to {self.target_speed}")

    def stop_motor(self, instance=None):
        if self.motor_armed:
            self.motor_rotor.idle()
            self.motor_armed = False
            print("Motor stopped.")
        self.running = False

    def on_stop(self):
        self.stop_motor()
        self.data_thread.join()
        self.export_data()

    def export_data(self):
        with open('motor_test_data_with_ui.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Time (s)', 'Motor Position', 'Motor Speed'])
            for i in range(len(self.times)):
                writer.writerow([self.times[i], self.position_readings[i], self.speed_readings[i]])
        print('Data exported to motor_test_data_with_ui.csv')

class MotorApp(App):
    def build(self):
        controller = MotorController()
        return controller

    def on_stop(self):
        self.root.on_stop()

if __name__ == '__main__':
    MotorApp().run()