#!/usr/bin/env python3

import time
import threading
import csv
from collections import deque

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.graph import Graph, MeshLinePlot
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.properties import NumericProperty

import matplotlib.pyplot as plt  # If you still want to use matplotlib
from cued_ia_lego import *  # Assuming this is your proprietary library

#from heli_programs.calibrate_lift import light_readings

# Constants
SMOOTHING_FACTOR = 0.05
DATA_DURATION = 60  # seconds to run the data collection

class MotorController(BoxLayout):
    target_power = NumericProperty(100)  # Default target speed
    target_pitch = NumericProperty(400)  # Default target speed

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
        self.motor_rotor = Motor(self.brick, PORT_A, power=self.target_power, speedreg=False, smoothstart=True, brake=False)
        self.motor_rotor.reset_position()

        # Set up pitch motor
        self.motor_pitch = Motor(self.brick, PORT_B, power=40, speedreg=True, smoothstart=True, brake=True)
        self.motor_pitch.reset_position()
        self.motor_pitch.turn_to(self.target_pitch)

        self.motor_rotor.run()
        self.motor_armed = True

        # Light sensor connected to sensor port 1, LED active
        self.light = Light(self.brick, PORT_1, illuminated=True)

        # Data storage
        self.times = deque(maxlen=2000)  # Store up to 2000 data points
        self.position_readings = deque(maxlen=2000)
        self.speed_readings = deque(maxlen=2000)
        self.light_readings=deque(maxlen=2000)

        # Set up Graph
        self.graph = Graph(
            xlabel='Time (s)', ylabel='Motor Speed',
            x_ticks_major=10, y_ticks_major=100,
            y_grid_label=True, x_grid_label=True,
            padding=5, x_grid=True, y_grid=True, xmin=0, xmax=60, ymin=0, ymax=800
        )


        self.plot = MeshLinePlot(color=[1, 0, 0, 1])
        self.graph.add_plot(self.plot)

        self.add_widget(self.graph)

        # Set up Graph 2 - Light sensor readings
        self.graphLight = Graph(
            xlabel='Time (s)', ylabel='Light Sensor Readings',
            x_ticks_major=10, y_ticks_major=100,
            y_grid_label=True, x_grid_label=True,
            padding=5, x_grid=True, y_grid=True, xmin=0, xmax=60, ymin=0, ymax=800
        )

        self.plotLight = MeshLinePlot(color=[0, 1,0,1])
        self.graphLight.add_plot(self.plotLight)    #to add to original graph, just do self.graph.add_lot(self.plotDIFFERENTNAME)

        self.add_widget(self.graphLight)

        # Set up Buttons
        button_layout = BoxLayout(size_hint_y=0.2)

        self.btn_increase = Button(text='Increase Speed')
        self.btn_decrease = Button(text='Decrease Speed')
        self.btn_stop = Button(text='Stop Motor')
        self.btn_increasePitch = Button(text='Increase Pitch')
        self.btn_decreasePitch = Button(text='Decrease Pitch}')

        self.btn_increase.bind(on_press=self.increase_speed)
        self.btn_decrease.bind(on_press=self.decrease_speed)
        self.btn_stop.bind(on_press=self.stop_motor)
        self.btn_increasePitch.bind(on_press=self.increase_pitch)
        self.btn_decreasePitch.bind(on_press=self.decrease_pitch)

        button_layout.add_widget(self.btn_increase)
        button_layout.add_widget(self.btn_decrease)
        button_layout.add_widget(self.btn_stop)
        button_layout.add_widget(self.btn_increasePitch)
        button_layout.add_widget(self.btn_decreasePitch)

        self.add_widget(button_layout)

        # Start Data Collection Thread
        self.running = True
        self.start_time = time.perf_counter()
        self.data_thread = threading.Thread(target=self.collect_data)
        self.data_thread.start()

        # Schedule Graph Update
        Clock.schedule_interval(self.update_graph, 1.0 / 30.0)  # 30 FPS

    def collect_data(self): #async running
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

            # Apply smoothing (one-sided moving average)
            if self.speed_readings:
                smoothed_speed = (1 - SMOOTHING_FACTOR) * self.speed_readings[-1] + SMOOTHING_FACTOR * speed
            else:
                smoothed_speed = speed

            self.speed_readings.append(smoothed_speed)

            # Calculate one sided moving average of light reading and append, using the smoothing factor logic
            current_light_reading = self.light.get_lightness()
            if len(self.light_readings) > 1:
                #d_time = self.times[-1] - self.times[-2]
                self.light_readings.append(self.light_readings[-1]*(1- SMOOTHING_FACTOR) + current_light_reading*SMOOTHING_FACTOR)


            else:
                self.light_readings.append(current_light_reading)


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

            self.plotLight.points = list(zip(self.times, self.light_readings))




    def increase_speed(self, instance):
        self.target_power += 10
        if self.target_power > 100: #strictly larger than
            self.target_power = 100  # Maximum speed limit
        self.motor_rotor.run(power=self.target_power)
        print(f"Target speed increased to {self.target_power}")

    def decrease_speed(self, instance):
        self.target_power -= 10
        if self.target_power < 0:
            self.target_power = 0  # Minimum speed limit
        self.motor_rotor.run(power=self.target_power)
        print(f"Target speed decreased to {self.target_power}")

    def increase_pitch(self, instance):
        self.target_pitch += 100
        if self.target_pitch > 900: #strictly larger than
            self.target_pitch = 900  # Maximum speed limit
        self.motor_pitch.turn_to(-self.target_pitch)
        print(f"Target pitch increased to {self.target_pitch}")

    def decrease_pitch(self, instance):
        self.target_pitch -= 100
        if self.target_pitch < 0:
            self.target_pitch = 0  # Minimum speed limit
        self.motor_pitch.turn_to(-self.target_pitch)
        print(f"Target pitch decreased to {self.target_pitch}")

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