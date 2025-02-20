from particle_simulation.main_classes import Particle

class Particle_A(Particle):
    def __init__(self, position):
        super().__init__(position)
        self.particle_label = "Particle_A"
        self.type_id = 0
        self.influence_strength = 1
        self.step_size = 0.5
        self.influence_radius = 1
        self.color = Particle.generate_particle_colors(self.particle_label, 1)[0]

class Particle_B(Particle):
    def __init__(self, position):
        super().__init__(position)
        self.particle_label = "Particle_B"
        self.type_id = 1
        self.influence_strength = 1
        self.step_size = 0.5
        self.influence_radius = 1
        self.color = Particle.generate_particle_colors(self.particle_label, 1)[0]

class Particle_C(Particle):
    def __init__(self, position):
        super().__init__(position)
        self.particle_label = "Particle_C"
        self.type_id = 2
        self.influence_strength = 1
        self.step_size = 0.5
        self.influence_radius = 1
        self.color = Particle.generate_particle_colors(self.particle_label, 1)[0]

class Particle_D(Particle):
    def __init__(self, position):
        super().__init__(position)
        self.particle_label = "Particle_D"
        self.type_id = 3
        self.influence_strength = 1
        self.step_size = 0.5
        self.influence_radius = 1
        self.color = Particle.generate_particle_colors(self.particle_label, 1)[0]
