# This file is used to automatically test python functions and code in students' work for NB9.

import numpy as np

def check_E_T(namespace, plots):

    E_T = namespace.get("E_T")
    if E_T is None:
        raise ValueError("E_T() not defined")

    h = namespace.get("h")
    c = namespace.get("c")
    a = namespace.get("a")

    if any(x is None for x in (h, c, a)):
        raise ValueError("Constants h, c or a not defined")

    test_cases = [
        (1e-6, 1),
        (1e-6, 5),
        (2e-6, 10),
        (5e-7, 20),
    ]

    for l0, N in test_cases:

        expected = 0.0

        for i in range(1, N + 1):
            expected += l0 / (
                (i * l0)**5 * np.expm1(a / (i * l0))
            )

        expected *= 2 * np.pi * h * c**2

        result = E_T(l0, N)

        np.testing.assert_allclose(
            result,
            expected,
            rtol=1e-6,
            err_msg=f"Incorrect E_T for l0={l0}, N={N}"
        )

def check_E_T_2(namespace, plots):

    E_T_2 = namespace.get("E_T_2")
    if E_T_2 is None:
        raise ValueError("E_T_2() not defined")

    h = namespace.get("h")
    c = namespace.get("c")
    a = namespace.get("a")

    if any(x is None for x in (h, c, a)):
        raise ValueError("Constants h, c or a not defined")

    test_cases = [
        (1e-7, 1.1 * 1.602176634e-19),
        (2e-7, 1.1 * 1.602176634e-19),
        (5e-7, 0.8 * 1.602176634e-19),
        (1e-6, 0.5 * 1.602176634e-19),
    ]

    for l0, Eg in test_cases:

        N = int((h * c) / (Eg * l0))

        expected = 0.0

        for i in range(1, N):
            expected += 1 / (
                (i * l0)**4 * np.exp(a / (i * l0) - 1)
            )

        expected *= 2 * np.pi * c * Eg * l0

        result = E_T_2(l0, Eg)

        np.testing.assert_allclose(
            result,
            expected,
            rtol=1e-6,
            err_msg=f"Incorrect E_T_2 for l0={l0}, Eg={Eg}"
        )

def check_optimum(namespace, plots):

    optimum = namespace.get("optimum")

    if optimum is None:
        raise ValueError("optimum variable not defined")

    assert np.isscalar(optimum), (
        "optimum must be a scalar value"
    )

    assert np.isfinite(optimum), (
        "optimum must be a finite number"
    )

    assert 1.05 <= optimum <= 1.15, (
        f"Does not conform to expected range. "
        f"got {optimum}."
    )