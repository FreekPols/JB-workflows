# This file is used to automatically test python functions and code in students' work for NB2.

import numpy as np

def check_brownian_distance_histogram_solution(source):
    """Check the solution for exercise 15: Afgelegde weg."""

    assert "361" in source, (
        "Gebruik 361 deeltjes voor deze oefening."
    )

    assert "hist(" in source, (
        "Maak een histogram van de afgelegde afstanden."
    )

    assert "vlines(" in source or "axvline(" in source, (
        "Markeer de afgelegde afstand van het zware deeltje."
    )

