import numpy as np


def check_tempfun(temperature_function):

    class FakeParticle:
        def __init__(self, kin_energy):
            self.kin_energy = kin_energy

    test_cases = [
        # kinetic energies, expected temperature
        ([10], 10),                 # One particle
        ([10, 20], 15),             # Two particles
        ([10, 20, 30], 20),         # Three particles
        ([0, 0, 0], 0),             # No kinetic energy
        ([2, 4, 9], 5),             # Unequal energies
        ([0.5, 1.5, 4.0], 2),       # Floating-point values
        ([1, 2, 3, 10], 4),         # Different number of particles
    ]

    for energies, expected in test_cases:

        particles = [
            FakeParticle(energy)
            for energy in energies
        ]

        result = temperature_function(particles)

        np.testing.assert_allclose(
            result,
            expected,
            err_msg=(
                f"Incorrect temperature for "
                f"kinetic energies {energies}"
            )
        )



def check_const_temp(temperatures):

    temperatures = np.asarray(temperatures, dtype=float)

    # Check that temperatures have been recorded
    assert temperatures.size == 100, (
        f"Expected 100 temperature measurements, "
        f"got {temperatures.size}."
    )

    # Check for invalid values
    assert np.all(np.isfinite(temperatures)), (
        "Temperature array contains NaN or infinite values."
    )

    # Check that temperature remains between 290 and 300 K
    assert np.all((temperatures >= 290) & (temperatures <= 300)), (
        f"Temperature should remain between 290 and 300 K. "
        f"Minimum: {temperatures.min():.2f} K, "
        f"maximum: {temperatures.max():.2f} K."
    )        

def check_plot_pres(pressures, calls):

    expected = np.arange(1, 101, dtype=float)

    # Check initialization
    assert calls["create"] == 1, (
        "create_particles() should be called exactly once."
    )

    # Check number of time steps
    assert calls["steps"] == 100, (
        f"Expected 100 time steps, got {calls['steps']}."
    )

    # Check that pressure is recorded at every time step
    np.testing.assert_allclose(
        pressures,
        expected,
        err_msg="Pressure was not recorded correctly at each time step."
    )