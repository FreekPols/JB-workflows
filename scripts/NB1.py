# This file is used to automatically test python functions and code in students' work.

import numpy as np

## First check
def check_doorlopende_doos(update_function):
    class FakeParticle:
        def __init__(self):
            self.r = np.array([0.0, 0.0])

        def update_position(self):
            # We test only the boundary logic.
            pass

    class FakeDot:
        def set_data(self, x, y):
            pass

    particle = FakeParticle()
    dot = FakeDot()

    # Make particle and dot available to update()
    update_function.__globals__["particle"] = particle
    update_function.__globals__["dot"] = dot

    test_cases = [
        # initial_x, expected_x
        (0, 0),        # Inside the box
        (5, 5),        # Inside the box
        (-5, -5),      # Inside the box
        (11, -11),     # Outside right boundary
        (-11, 11),     # Outside left boundary
        (10, -10),     # Exactly at right boundary
        (-10, 10),     # Exactly at left boundary
    ]

    for initial_x, expected_x in test_cases:

        particle.r[0] = initial_x
        particle.r[1] = 0

        update_function(0)

        np.testing.assert_allclose(particle.r[0], expected_x, err_msg=f"Incorrect boundary handling for x={initial_x}")

## Second check
def check_harde_wanden(update_function):

    class FakeParticle:
        def __init__(self):
            self.r = np.array([0.0, 0.0])
            self.v = np.array([0.0, 0.0])

        def update_position(self):
            # We test only the boundary logic.
            pass

    class FakeDot:
        def set_data(self, x, y):
            pass

    particle = FakeParticle()
    dot = FakeDot()

    # Make particle and dot available to update()
    update_function.__globals__["particle"] = particle
    update_function.__globals__["dot"] = dot

    test_cases = [
        # initial_x, initial_vx, expected_vx
        (0,     5,    5),    # Inside box: velocity unchanged
        (9,    -5,   -5),    # Inside box: velocity unchanged
        (11,    5,   -5),    # Outside right: reverse velocity
        (-11,  -5,    5),    # Outside left: reverse velocity
    ]

    for initial_x, initial_vx, expected_vx in test_cases:

        particle.r[0] = initial_x
        particle.r[1] = 0

        particle.v[0] = initial_vx
        particle.v[1] = 0

        update_function(0)

        np.testing.assert_allclose(
            particle.v[0],
            expected_vx,
            err_msg=(
                f"Incorrect wall reflection for "
                f"x={initial_x}, vx={initial_vx}"
            )
        )

## Third check
def check_botsingsvoorwaarde(ParticleClass):

    # Test cases:
    # (position1, radius1, position2, radius2, expected)

    test_cases = [
        ([0, 0], 1, [0, 0], 1, True),      # Same position
        ([0, 0], 1, [1, 0], 1, True),      # Overlap horizontally
        ([0, 0], 1, [0, 1], 1, True),      # Overlap vertically
        ([0, 0], 1, [3, 0], 1, False),     # No collision
        ([0, 0], 1, [0, 3], 1, False),     # No collision
        ([0, 0], 1, [1, 1], 1, True),      # Diagonal overlap
        ([0, 0], 1, [2, 0], 1, False),     # Exactly touching
        ([0, 0], 2, [2, 0], 1, True),      # Different radii
        ([-3, -4], 1, [-3, -7], 1, False), # Negative coordinates
    ]

    for r1, R1, r2, R2, expected in test_cases:

        # Create two particles
        particle1 = ParticleClass(m=1,v=[0, 0],r=r1,R=R1)
        particle2 = ParticleClass(m=1,v=[0, 0],r=r2,R=R2)

        # Call the student's collision detection method
        result = particle1.collide_detection(particle2)

        assert bool(result) == expected, (
            f"Incorrect collision detection for "
            f"r1={r1}, R1={R1}, r2={r2}, R2={R2}. "
            f"Expected {expected}, got {result}."
        )