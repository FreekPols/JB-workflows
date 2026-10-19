import numpy as np


def check_uniform_particles(create_uniform_particles):

    # Test parameters
    N = 20
    V_0 = 5.0
    RADIUS = 0.5
    BOX_SIZE_0 = 10.0

    class FakeParticle:
        def __init__(self, m, v, r, R):
            self.m = m
            self.v = np.asarray(v, dtype=float)
            self.r = np.asarray(r, dtype=float)
            self.R = R

    # Make required variables available to the student's function
    namespace = create_uniform_particles.__globals__

    namespace["N"] = N
    namespace["V_0"] = V_0
    namespace["RADIUS"] = RADIUS
    namespace["BOX_SIZE_0"] = BOX_SIZE_0
    namespace["ParticleClass"] = FakeParticle
    namespace["np"] = np

    # Add an existing particle to check whether the list is cleared
    old_particle = FakeParticle(
        m=1.0,
        v=[99, 99],
        r=[0, 0],
        R=RADIUS
    )

    particles = [old_particle]

    # Run the student's function
    create_uniform_particles(particles)

    # Check that the original list was cleared
    assert old_particle not in particles, (
        "The existing particles were not removed."
    )

    # Check the number of particles
    assert len(particles) == N, (
        f"Expected {N} particles, got {len(particles)}."
    )

    # Check properties of every particle
    lower_bound = -BOX_SIZE_0 / 2 + RADIUS
    upper_bound = BOX_SIZE_0 / 2 - RADIUS

    for i, particle in enumerate(particles):

        assert isinstance(particle, FakeParticle), (
            f"Particle {i} was not created with ParticleClass."
        )

        np.testing.assert_allclose(
            particle.v,
            [0, V_0],
            err_msg=f"Particle {i} has incorrect initial velocity."
        )

        np.testing.assert_allclose(
            particle.m,
            1.0,
            err_msg=f"Particle {i} has incorrect mass."
        )

        np.testing.assert_allclose(
            particle.R,
            RADIUS,
            err_msg=f"Particle {i} has incorrect radius."
        )

        assert particle.r.shape == (2,), (
            f"Particle {i} should have a 2D position."
        )

        assert np.all(
            (particle.r >= lower_bound) &
            (particle.r <= upper_bound)
        ), (
            f"Particle {i} is outside the allowed box boundaries."
        )