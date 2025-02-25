import random
import math
from vispy import app
import numpy as np
from numba import njit, prange
import pyautogui


@njit(parallel=True)
def move_particles_numba(positions, step_sizes, width, height):
    """Parallele Bewegung der Partikel mit Numba und prange."""
    n = len(positions)
    for i in prange(n):
        step_size = step_sizes[i]
        positions[i, 0] = (positions[i, 0] + np.random.uniform(-step_size, step_size)) % width
        positions[i, 1] = (positions[i, 1] + np.random.uniform(-step_size, step_size)) % height


class ParticleField:
    def __init__(self, width, height, num_particles):
        self.width = width
        self.height = height
        self.num_particles = num_particles
        self.spatial_hash = SpatialHashGrid(cell_size=2)
        self.particles = self.generate_particles()
        

    def generate_particles(self):
        from particle_simulation.particle_classes import Particle_A, Particle_B, Particle_C, Particle_D

        particles_list = []
        grid_size = math.ceil(self.num_particles**0.5)
        spacing_x = self.width / grid_size
        spacing_y = self.height / grid_size

        for i in range(grid_size):
            for j in range(grid_size):
                if len(particles_list) < self.num_particles:
                    x = (i + 0.5) * spacing_x
                    y = (j + 0.5) * spacing_y
                    particle_type = random.choice([Particle_A, Particle_B, Particle_C, Particle_D])
                    particle = particle_type((x, y))
                    particles_list.append(particle)
                    self.spatial_hash.insert(particle)
        return particles_list

    def update_particles(self):
        positions = np.array([p.position for p in self.particles], dtype=np.float32)
        step_sizes = np.array([p.step_size for p in self.particles], dtype=np.float32)

        move_particles_numba(positions, step_sizes, self.width, self.height)

        

        for i, particle in enumerate(self.particles):
            old_cell = self.spatial_hash._hash(particle.position)
            particle.position = (positions[i, 0], positions[i, 1])
            new_cell = self.spatial_hash._hash(particle.position)

            # Nur aktualisieren, wenn sich die Zelle geändert hat
            if old_cell != new_cell:
                self.spatial_hash.remove(particle)
                self.spatial_hash.insert(particle)




    def start_movement(self, interaction_options):
        effect = interaction_effects(self.particles, interaction_options)

        def update(event):
            self.update_particles()
            effect.build_spatial_index()


        if hasattr(self, 'timer') and self.timer.running:
            self.timer.stop()

        self.timer = app.Timer(interval=0.02, connect=update, start=True)

    def add_particles(self, count):
        """Fügt eine bestimmte Anzahl an Partikeln hinzu."""
        from particle_simulation.particle_classes import Particle_A, Particle_B, Particle_C, Particle_D
        particle_types = [Particle_A, Particle_B, Particle_C, Particle_D]

        for _ in range(count):
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.height)
            particle_type = random.choice(particle_types)
            self.particles.append(particle_type((x, y)))
            self.spatial_hash.insert(particle_type((x, y)))
            
        




    def remove_particles(self, count):
        """Entfernt zufällige Partikel und aktualisiert die Hashmap."""
        if count > len(self.particles):
            count = len(self.particles)

        indices_to_remove = random.sample(range(len(self.particles)), count)
        particles_to_remove = [self.particles[i] for i in indices_to_remove]

        # Entfernen aus Hashmap und Partikel-Liste
        for particle in particles_to_remove:
            self.spatial_hash.remove(particle)  # Entferne aus Hashmap
            self.particles.remove(particle)



class Particle:
    def __init__(self, position):
        self.particle_label = None
        self.position = position
        self.step_size = 0.05
        self.influence_strength = random.uniform(0, 1)**2
        self.influence_radius = None
        self.color = None

    @staticmethod
    def generate_particle_colors(particle_type, iterations):
        color_schemes = {
            "Particle_A": lambda: (np.random.uniform(0.9, 1.0), np.random.uniform(0.9, 1.0), np.random.uniform(0.9, 1.0)),
            "Particle_B": lambda: (np.random.uniform(0.97, 1.0), np.random.uniform(0.95, 1.0), np.random.uniform(0.6, 0.8)),
            "Particle_C": lambda: (np.random.uniform(0.4, 0.6), np.random.uniform(0.8, 0.95), np.random.uniform(0.9, 1.0)),
            "Particle_D": lambda: (np.random.uniform(0.7, 0.85), np.random.uniform(0.6, 0.75), np.random.uniform(0.85, 1.0)),
        }

        if particle_type not in color_schemes:
            raise ValueError(f"Unknown particle type: {particle_type}")

        unique_colors = np.array([color_schemes[particle_type]() for _ in range(iterations)], dtype=np.float32)
        return unique_colors

class interaction_effects:
    def __init__(self, particles, interaction_options):
        self.particles = particles
        self.interactions = InteractionMatrix(interaction_options)
        self.spatial_hash = None
        self.build_spatial_index()


    def attract_particles(self, repulsion_enabled):
        pass

    def repel_particles(self, repulsion_enabled):
        pass

    def build_spatial_index(self):
        """Erstellt die Spatial Hashmap."""
        cell_size = 2  # Zellengröße, anpassen für Performance:
                        # Kleinerer Wert (z. B. 2 oder 3): Mehr, aber kleinere Zellen. Gut bei vielen Partikeln mit kleinem Einflussradius, kann aber langsamer werden, wenn zu viele Zellen entstehen.
                        # Größerer Wert (z. B. 10 oder 20): Weniger, aber größere Zellen. Gut bei wenigen Partikeln mit großem Einflussradius, aber weniger genau bei Nachbarschaftssuch)
        self.spatial_hash = SpatialHashGrid(cell_size)
        for particle in self.particles:
            self.spatial_hash.insert(particle)
        print(f"Spatial Hashmap enthält {sum(len(v) for v in self.spatial_hash.grid.values())} Partikel in {len(self.spatial_hash.grid)} Zellen.")


    def find_particles_within_reactionradius(self, main_particle):
        """Sucht Nachbarpartikel mit Spatial Hashing."""
        max_neighbors = 20 # =None für unbegrenzt 
        neighbors = self.spatial_hash.query(main_particle.position, main_particle.influence_radius)
        print(f"Partikel bei {main_particle.position} hat {len(neighbors)} Nachbarn")
        return neighbors[:max_neighbors]

class InteractionMatrix:
    def __init__(self, interaction_options):
        self.matrix = np.zeros((4, 4), dtype=bool)
        labels = {"A": 0, "B": 1, "C": 2, "D": 3}

        for key, value in interaction_options.items():
            p1, p2 = key.split("_")
            self.matrix[labels[p1], labels[p2]] = value
            self.matrix[labels[p2], labels[p1]] = value

    def is_interaction_enabled(self, p1, p2):
        return self.matrix[p1, p2]

class SpatialHashGrid:
    """Spatial Hashing für schnelle Nachbarsuche."""
    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.grid = {}

    def _hash(self, position):
        """Berechnet den Hash-Wert basierend auf der Zellengröße."""
        return (int(position[0] // self.cell_size), int(position[1] // self.cell_size))

    def insert(self, particle):
        """Fügt ein Partikel in die entsprechende Zelle der Hashmap ein."""
        cell = self._hash(particle.position)
        if cell not in self.grid:
            self.grid[cell] = []
        self.grid[cell].append(particle)

    def clear(self):
        """Leert die gesamte Hashmap."""
        self.grid = {}

    def remove(self, particle):
        """Entfernt ein Partikel aus der entsprechenden Zelle der Hashmap."""
        cell = self._hash(particle.position)
        if cell in self.grid:
            try:
                self.grid[cell].remove(particle)
                if not self.grid[cell]:  #Zelle löschen, wenn sie leer ist
                    del self.grid[cell]
            except ValueError:
                pass  #Partikel nicht gefunden, ignorieren

    def query(self, position, radius):
        """Sucht alle Partikel in umliegenden Zellen, die innerhalb des Radius liegen."""
        found_particles = []
        radius_cells = int(radius // self.cell_size) + 1
        center_cell = self._hash(position)

        for dx in range(-radius_cells, radius_cells + 1):
            for dy in range(-radius_cells, radius_cells + 1):
                cell = (center_cell[0] + dx, center_cell[1] + dy)
                if cell in self.grid:
                    for particle in self.grid[cell]:
                        dist_sq = (particle.position[0] - position[0])**2 + (particle.position[1] - position[1])**2
                        if dist_sq <= radius**2:
                            found_particles.append(particle)

        return found_particles
    


#TO Do
#SICHERSTELLEN DASS HASHMAP AKTUALISIERT WIRD WENN DIE ANZAHL VON PARTICLES GESTEUERT WIRD 
#MAYBE PARTICLES IN DEN HASHMAPS PACKEN DIREKT BEIM GENERIERUNG ?