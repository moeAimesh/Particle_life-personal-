import time
import os
# Erst jetzt VisPy importieren!
from vispy import scene, app
from vispy.scene import visuals
import numpy as np
import sys

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
