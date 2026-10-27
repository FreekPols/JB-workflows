# This file is used to automatically test python functions and code in students' work for NB2.

import numpy as np
import matplotlib
from matplotlib.collections import LineCollection

    
def check_brownian_distance_histogram_solution(namespace, plots):
    """Check the solution for exercise 15: Afgelegde weg."""

    # check at least one plot was created
    assert len(plots) == 1, f"Expected 1 plot, found {len(plots)}."

    # check plot contains a histogram
    plot = plots[0]
    assert len(plot.patches) > 0, "Plot must contain a histogram."

    # check if there is a np array defined which has shape (361,) do not assume any variable name, but check all variables in the namespace
    distance_arrays = [value for value in namespace.values() if isinstance(value, np.ndarray) and value.shape == (361,)]
    assert len(distance_arrays) > 0, "No distance array found with 361 elements."
    
    has_vline = any(l.get_xdata()[0] == l.get_xdata()[1] for l in plot.lines) or any(isinstance(c, LineCollection) for c in plot.collections)
    assert has_vline, "No vertical line found in the plot."

def check_ex7(namespace, plots):
    assert len(plots) == 1, f"Expected 1 plot, found {len(plots)}."
    plot = plots[0]
    assert plot.get_xlabel() != "" and plot.get_ylabel() != "", "Plot must have x and y labels."
    assert len(plot.lines) > 0, "Plot must not be empty."
