import time
import numpy as np
from numba import njit, prange

#Particle-Klasse für den Test
class Particle:
    def __init__(self, position):
        self.position = position

# Spatial Hashmap-Klasse
class SpatialHashGrid:
    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.grid = {}

#Variante 1: Batch-Insert mit NumPy
def build_spatial_index_numpy(particles, cell_size):
    spatial_hash = SpatialHashGrid(cell_size)
    positions = np.array([p.position for p in particles], dtype=np.float32)
    cell_keys = ((positions[:, 0] // cell_size).astype(int), (positions[:, 1] // cell_size).astype(int))
    unique_cells, indices = np.unique(np.column_stack(cell_keys), axis=0, return_inverse=True)

    for i, cell in enumerate(unique_cells):
        spatial_hash.grid[tuple(cell)] = [particles[j] for j in np.where(indices == i)[0]]
    return spatial_hash


#Variante 2: Parallele Verarbeitung mit Numba
@njit(parallel=True)
def calculate_cell_indices(positions, cell_size):
    n = len(positions)
    cell_indices = np.empty((n, 2), dtype=np.int32)
    for i in prange(n):
        cell_indices[i, 0] = int(positions[i, 0] // cell_size)
        cell_indices[i, 1] = int(positions[i, 1] // cell_size)
    return cell_indices

def build_spatial_index_numba(particles, cell_size):
    spatial_hash = SpatialHashGrid(cell_size)
    positions = np.array([p.position for p in particles], dtype=np.float32)
    cell_indices = calculate_cell_indices(positions, cell_size)

    for idx, particle in zip(cell_indices, particles):
        cell = tuple(idx)
        if cell not in spatial_hash.grid:
            spatial_hash.grid[cell] = []
        spatial_hash.grid[cell].append(particle)
    return spatial_hash


#Variante 3: Direkte NumPy-Lösung
def build_spatial_index_numpy_direct(particles, cell_size):
    spatial_hash = SpatialHashGrid(cell_size)
    positions = np.array([p.position for p in particles], dtype=np.float32)
    cell_keys = (positions[:, 0] // cell_size, positions[:, 1] // cell_size)
    cells = np.stack(cell_keys, axis=1).astype(int)

    unique_cells, indices = np.unique(cells, axis=0, return_inverse=True)
    for cell, idx in zip(unique_cells, range(len(unique_cells))):
        spatial_hash.grid[tuple(cell)] = [particles[i] for i in np.where(indices == idx)[0]]
    return spatial_hash


# Benchmark-Funktion
def benchmark(func, particles, cell_size, iterations=10):
    """Misst die durchschnittliche Laufzeit einer Funktion."""
    total_time = 0
    for _ in range(iterations):
        start = time.perf_counter()
        func(particles, cell_size)
        end = time.perf_counter()
        total_time += end - start
    avg_time = total_time / iterations
    print(f"{func.__name__} average time: {avg_time:.6f} seconds")


# Testdaten
n = 50000  # Anzahl der Partikel
particles = [Particle((np.random.uniform(0, 1000), np.random.uniform(0, 1000))) for _ in range(n)]
cell_size = 2
cell_size2= 20

# Warm-Up für Numba (JIT-Kompilierung)
build_spatial_index_numba(particles, cell_size)
build_spatial_index_numba(particles, cell_size2)

# Benchmark-Ausführung
print("\nBenchmark Results:")
benchmark(build_spatial_index_numpy, particles, cell_size)
benchmark(build_spatial_index_numba, particles, cell_size)
benchmark(build_spatial_index_numpy_direct, particles, cell_size)

print("\nBenchmark Results2:")
benchmark(build_spatial_index_numpy, particles, cell_size2)
benchmark(build_spatial_index_numba, particles, cell_size2)
benchmark(build_spatial_index_numpy_direct, particles, cell_size2)


#numba ist schneller egal wie gross cell_size wird !