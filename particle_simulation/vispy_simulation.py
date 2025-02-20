import os
import sys
import random

import time
from vispy import scene, app
from vispy.scene import visuals
import numpy as np

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QVBoxLayout, QSlider, QLabel, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt


# Füge den richtigen Pfad für `particle_simulation` hinzu
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../particle_simulation')))





class VisPyCanvas(scene.SceneCanvas):
    def __init__(self, particle_field, width, height, scale=1.0):
        super().__init__(keys='interactive', size=(width, height))  # Bildschirmgröße setzen

        self.unfreeze()
        self.particle_field = particle_field
        self.scale = scale


        self.view = self.central_widget.add_view()
        self.view.camera = scene.cameras.PanZoomCamera(aspect=1)
        self.view.camera.set_range(x=(0, particle_field.width), y=(0, particle_field.height))


        self.particles = visuals.Markers()
        self.view.add(self.particles)


        self.last_time = time.time()
        self.timer = app.Timer(interval=0.01, connect=self.update_particles, start=True)
        self.init_particles()


        self.freeze()

    def init_particles(self):
        """Erstellt das Partikel-System mit VisPy."""
        positions = np.array([p.position for p in self.particle_field.particles], dtype=np.float32)
        colors = np.array([p.color for p in self.particle_field.particles], dtype=np.float32)

        self.particles.set_data(pos=positions, face_color=colors, size=7, edge_width=0, edge_color=None)


    def update_particles(self, event):
        """FPS-basiertes Update für mehr Smoothness."""
        current_time = time.time()
        dt = current_time - self.last_time  # Delta-Time berechnen
        self.last_time = current_time  # Update Zeitstempel

        self.particle_field.update_particles()  # Simuliere Bewegung
        positions = np.array([p.position for p in self.particle_field.particles], dtype=np.float32)
        colors = np.array([p.color for p in self.particle_field.particles], dtype=np.float32)
        self.particles.set_data(pos=positions, size=7, face_color=colors)  # VisPy Rendering

        app.process_events()  # Verhindert Framedrops
        time.sleep(max(0.01 - dt, 0))  # FPS stabilisieren

        
    def update_particle_count(self, new_count):
        """Fügt Partikel hinzu oder entfernt sie, ohne die Simulation neu zu starten."""
        current_count = len(self.particle_field.particles)

        if new_count > current_count:
            # ➕ Partikel hinzufügen
            self.particle_field.add_particles(new_count - current_count)
        elif new_count < current_count:
            # ➖ Partikel entfernen
            self.particle_field.remove_particles(current_count - new_count)

        self.init_particles()






class MainWindow(QWidget):
    """PyQt-Fenster mit VisPy-Canvas und Slider."""
    def __init__(self, particle_field, width, height):
        super().__init__()
        self.setWindowTitle("Particle Simulation mit Slider")
        self.resize(width, height + 100)

        self.particle_field = particle_field
        self.canvas = VisPyCanvas(particle_field, width, height)

        self.init_ui()

    def init_ui(self):
        """Erstellt die GUI mit VisPy-Canvas und Slider."""
        layout = QVBoxLayout()

        # VisPy-Canvas hinzufügen
        layout.addWidget(self.canvas.native)

        # Horizontaler Bereich für Slider und Label
        slider_layout = QHBoxLayout()

        # Label zur Anzeige der Partikelanzahl
        self.label = QLabel(f"Partikelanzahl: {self.particle_field.num_particles}")
        self.label.setAlignment(Qt.AlignCenter)
        slider_layout.addWidget(self.label)

        # Slider zur Steuerung der Partikelanzahl
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(50)
        self.slider.setMaximum(50000)
        self.slider.setValue(self.particle_field.num_particles)
        self.slider.setTickInterval(5000)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.valueChanged.connect(self.on_slider_change)
        slider_layout.addWidget(self.slider)

        layout.addLayout(slider_layout)
        self.setLayout(layout)

    def on_slider_change(self, value):
        """Aktualisiert die Partikelanzahl bei Slider-Bewegung."""
        self.label.setText(f"Partikelanzahl: {value}")
        self.canvas.update_particle_count(value)



def start_simulation(field, width, height):
    """Startet die VisPy-App-Schleife mit PyQt."""
    app_qt = QtWidgets.QApplication.instance()
    if app_qt is None:
        app_qt = QtWidgets.QApplication(sys.argv)  # Nur erstellen, wenn sie nicht existiert

    window = MainWindow(field, width, height)
    window.show()

    app_qt.aboutToQuit.connect(app.quit)  # Beendet VisPy, wenn PyQt geschlossen wird
    app.run()  # VisPy-App-Schleife starten