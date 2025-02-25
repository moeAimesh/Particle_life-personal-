import timeit
import numpy as np
from numba import njit, prange

# Funktionen definieren
@njit(parallel=True)
def move_particles_numba(positions, step_sizes, width, height):
    n = len(positions)
    for i in prange(n):
        step_size = step_sizes[i]
        positions[i, 0] = (positions[i, 0] + np.random.uniform(-step_size, step_size)) % width
        positions[i, 1] = (positions[i, 1] + np.random.uniform(-step_size, step_size)) % height

def move_particles_numpy(positions, step_sizes, width, height):
    n = len(positions)
    random_x = np.random.uniform(-step_sizes, step_sizes, size=n)
    random_y = np.random.uniform(-step_sizes, step_sizes, size=n)
    positions[:, 0] = (positions[:, 0] + random_x) % width
    positions[:, 1] = (positions[:, 1] + random_y) % height

def move_particles(positions, step_sizes, width, height):
    # Schneller: direkt Positionen updaten, ohne zwei separate Uniform-Aufrufe
    random_offsets = np.random.uniform(-1, 1, size=(len(positions), 2)) * step_sizes[:, None]
    positions[:] = (positions + random_offsets) % [width, height]

# Testdaten
n = 20000
positions = np.random.rand(n, 2) * 1000
step_sizes = np.random.rand(n) * 5
width, height = 1000, 1000

# Benchmark
print("Numba:")
print(timeit.timeit(lambda: move_particles_numba(positions.copy(), step_sizes, width, height), number=10))

print("NumPy:")
print(timeit.timeit(lambda: move_particles_numpy(positions.copy(), step_sizes, width, height), number=10))

print("Numpy2")
print(timeit.timeit(lambda: move_particles(positions.copy(), step_sizes, width, height), number=10))