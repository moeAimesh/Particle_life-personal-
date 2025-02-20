import random
import math
from vispy import app
import numpy as np
from numba import njit
import pyautogui

@njit(parallel=True)
def move_particles_numba(positions, step_sizes, width, height):
    for i in range(len(positions)):
        positions[i, 0] = (positions[i, 0] + np.random.uniform(-step_sizes[i], step_sizes[i])) % width
        positions[i, 1] = (positions[i, 1] + np.random.uniform(-step_sizes[i], step_sizes[i])) % height

class ParticleField:
    def __init__(self, width, height, num_particles):
        self.width = width
        self.height = height
        self.num_particles = num_particles
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
                    particles_list.append(particle_type((x, y)))
        return particles_list

    def update_particles(self):
        positions = np.array([p.position for p in self.particles], dtype=np.float32)
        step_sizes = np.array([p.step_size for p in self.particles], dtype=np.float32)

        move_particles_numba(positions, step_sizes, self.width, self.height)

        for i, particle in enumerate(self.particles):
            particle.position = (positions[i, 0], positions[i, 1])

    def start_movement(self, interaction_options):
        effect = interaction_effects(self.particles, interaction_options)

        def update(event):
            self.update_particles()
            effect.build_spatial_index()
            effect.attract_particles()

        self.timer = app.Timer(interval=0.02, connect=update, start=True)

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
        self.octree = None
        self.build_spatial_index()

    def attract_particles(self):
        pass

    def repel_particles(self, repulsion_enabled):
        pass

    def build_spatial_index(self):
        if hasattr(self, "update_counter") and self.update_counter % 10 != 0:
            return
        screen_width, screen_height = pyautogui.size()
        x_min, x_max, y_min, y_max = 0, screen_width, 0, screen_height
        self.octree = OctreeNode((x_min, x_max, y_min, y_max))

        for particle in self.particles:
            self.octree.insert(particle)

        self.update_counter = getattr(self, "update_counter", 0) + 1

    def find_particles_within_reactionradius(self, main_particle):
        max_neighbors = 20
        neighbors = self.octree.query(main_particle.position, main_particle.influence_radius)
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

class OctreeNode:
    def __init__(self, boundary, depth=0, max_depth=5, max_particles=10):
        self.boundary = boundary
        self.depth = depth
        self.max_depth = max_depth
        self.max_particles = max_particles
        self.particles = []
        self.children = []

    def insert(self, particle):
        if not self.contains(particle.position):
            return False

        if len(self.particles) < self.max_particles or self.depth >= self.max_depth:
            self.particles.append(particle)
            return True

        if not self.children:
            self.subdivide()

        for child in self.children:
            if child.insert(particle):
                return True

        return False

    def contains(self, position):
        x_min, x_max, y_min, y_max = self.boundary
        return x_min <= position[0] <= x_max and y_min <= position[1] <= y_max

    def subdivide(self):
        x_min, x_max, y_min, y_max = self.boundary
        x_mid = (x_min + x_max) / 2
        y_mid = (y_min + y_max) / 2

        self.children = [
            OctreeNode((x_min, x_mid, y_min, y_mid), self.depth + 1, self.max_depth, self.max_particles),
            OctreeNode((x_mid, x_max, y_min, y_mid), self.depth + 1, self.max_depth, self.max_particles),
            OctreeNode((x_min, x_mid, y_mid, y_max), self.depth + 1, self.max_depth, self.max_particles),
            OctreeNode((x_mid, x_max, y_mid, y_max), self.depth + 1, self.max_depth, self.max_particles),
        ]

    def query(self, position, radius, found_particles=None):
        if found_particles is None:
            found_particles = []

        if not self.intersects(position, radius):
            return found_particles

        for particle in self.particles:
            dist_sq = (particle.position[0] - position[0])**2 + (particle.position[1] - position[1])**2
            if dist_sq <= radius**2:
                found_particles.append(particle)

        for child in self.children:
            child.query(position, radius, found_particles)

        return found_particles

    def intersects(self, position, radius):
        x_min, x_max, y_min, y_max = self.boundary
        x, y = position

        nearest_x = max(x_min, min(x, x_max))
        nearest_y = max(y_min, min(y, y_max))
        dist_sq = (x - nearest_x) ** 2 + (y - nearest_y) ** 2

        return dist_sq <= radius ** 2
