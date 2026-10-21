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


def check_numsteps(source):

    test_cases = [
        # BOX_SIZE_0, V_0, DT
        (10.0, 2.0, 0.1),
        (20.0, 4.0, 0.2),
        (15.0, 3.0, 0.05),
        (12.0, 5.0, 0.3),
    ]

    for box_size, v0, dt in test_cases:

        namespace = {
            "BOX_SIZE_0": box_size,
            "V_0": v0,
            "DT": dt,
        }

        # Execute student's code with test parameters
        exec(source, namespace)

        assert "num_steps" in namespace, (
            "The variable num_steps was not defined."
        )

        expected = round(2 * box_size / (v0 * dt))
        result = namespace["num_steps"]

        assert result == expected, (
            f"Incorrect num_steps for BOX_SIZE_0={box_size}, "
            f"V_0={v0}, DT={dt}. "
            f"Expected {expected}, got {result}."
        )


def check_maxwell2d(maxwell2d):

    test_cases = [
        # v, a
        (0.0, 1.0),
        (0.5, 1.0),
        (1.0, 2.0),
        (2.0, 0.5),
        (3.0, 1.5),
    ]

    for v, a in test_cases:
        expected = a * v * np.exp(-a * v**2 / 2)
        result = maxwell2d(v, a)

        np.testing.assert_allclose(
            result,
            expected,
            rtol=1e-5,
            err_msg=f"Incorrect Maxwell distribution for v={v}, a={a}."
        )

    # Check that the function also supports NumPy arrays
    v = np.linspace(0, 5, 50)
    a = 1.5

    expected = a * v * np.exp(-a * v**2 / 2)
    result = maxwell2d(v, a)

    np.testing.assert_allclose(
        result,
        expected,
        rtol=1e-5,
        err_msg="maxwell2d() should support NumPy arrays."
    )


def check_maxwell_fit(popt):

    expected = 1.88190321
    tolerance = 0.15  # 15% relative tolerance

    popt = np.asarray(popt, dtype=float)

    assert popt.size >= 1, (
        "No fitted parameter found."
    )

    fitted_a = popt[0]

    np.testing.assert_allclose(
        fitted_a,
        expected,
        rtol=tolerance,
        err_msg=(
            f"Incorrect Maxwell fit parameter. "
            f"Expected approximately {expected:.4f}, "
            f"got {fitted_a:.4f}."
        )
    )

def check_excellent(source):
    # Ignore empty lines and comments
    lines = [
        line.strip()
        for line in source.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    assert lines, "The NB4_excellent cell is empty."