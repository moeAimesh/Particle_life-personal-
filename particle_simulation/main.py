from particle_simulation.main_classes import ParticleField
from particle_simulation.vispy_simulation import VisPyCanvas
from vispy import app
import pyautogui

# Bildschirmgröße abrufen
screen_width, screen_height = pyautogui.size()

if __name__ == "__main__":
    # Erstelle das Partikelfeld
    field = ParticleField(screen_width, screen_height, num_particles=20000)

    # Starte die VisPy-Visualisierung
    canvas = VisPyCanvas(field, screen_width, screen_height)

    # Starte die Partikelbewegung mit Interaktionsoptionen
    field.start_movement(interaction_options={
        "A_A": True,
        "A_B": False,
        "A_C": False,
        "A_D": False,
        "B_B": False,
        "B_C": False,
        "B_D": False,
        "C_C": False,
        "C_D": False,
        "D_D": False
    })

    # Zeige das VisPy-Fenster
    canvas.show()

    # Starte die VisPy-App-Schleife
    app.run()