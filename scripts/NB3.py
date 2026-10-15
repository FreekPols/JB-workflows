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