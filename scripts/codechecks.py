from pathlib import Path
import numpy as np
#import jupytext
import matplotlib
import sys
from checker import CodeChecker
matplotlib.use("Agg")

import matplotlib.pyplot as plt

from ctrlcv import check_written_solution

from NB1 import (
    check_doorlopende_doos,
    check_harde_wanden,
    check_botsingsvoorwaarde,
    check_eindantwoord,
)

from NB2 import (
    check_brownian_distance_histogram_solution,
    check_ex7,
)


from NB3 import (
    check_tempfun,
    check_const_temp,
    check_plot_pres,
)

from NB4 import (
    check_uniform_particles,
    check_numsteps,
    check_maxwell2d,
    check_maxwell_fit,
    check_excellent,
)

from NB9 import (
    check_E_T,
    check_E_T_2,
    check_optimum,
)

results = []


def check_cell(tag, notebook_path, test_function, init_tags=[], with_previous_cells=False):

    try:
        checker = CodeChecker(notebook_path)

        plots, namespace = checker.checkWithTag(tag, init_tags=init_tags, run_previous_cells=with_previous_cells)

        # Run the corresponding test from NB1.py
        test_function(namespace, plots)

        results.append((tag, True, ""))
        print(f"PASS: {tag}")

    except Exception as exc:
        results.append((tag, False, str(exc)))
        print(f"FAIL: {tag}: {exc}")

def check_written_answer(tag, notebook_path, test_function):

    try:
        answer = test_function(notebook_path, tag)

        results.append((tag, "REVIEW", answer))

        print(f"REVIEW: {tag}")

    except Exception as exc:
        results.append((tag, False, str(exc)))
        print(f"FAIL: {tag}: {exc}")
        

# Notebook file paths
notebook_file_paths = {
    "NB1": "simulations/NB1_deeltjesmodel.md",
    "NB2": "simulations/NB2_brownianmotion.md",
    "NB3": "simulations/NB3_druktemp.md",
    "NB4": "simulations/NB4_boltzmann.md",
    "NB9": "simulations/NB9_zonnecel.md",
}

NB1_cell_checks = [
    ("NB1_doorlopendedoos", check_doorlopende_doos, []),
    ("NB1_hardewand", check_harde_wanden, []),
    ("NB1_botsingsvoorwaarde", check_botsingsvoorwaarde, []),
    ("NB1_eindantwoord", check_eindantwoord, []),
]

NB2_cell_checks = [
    ("NB2_brownian_distance_histogram",
     check_brownian_distance_histogram_solution, ["NB2_init"]),
    ("NB2_ex7", check_ex7, ["NB2_init"]),
]

NB3_cell_checks = [
    ("NB3_tempfun", check_tempfun, []),
    ("NB3_check_const_temp", check_const_temp,
        ["NB3_init", "NB3_tempfun", ],),
    ("NB3_plot_pres", check_plot_pres, ["NB3_init", "NB3_init_ex4"]),
]

NB4_cell_checks = [
    ("NB4_uniform_particles", check_uniform_particles, []),
    ("NB4_numsteps", check_numsteps, ["NB4_init_1", "NB4_init_2", "NB4_init_3", "NB4_init_4","NB4_uniform_particles"]),
    ("NB4_maxwell2d", check_maxwell2d, ["NB4_init_1", "NB4_init_2", "NB4_init_3", "NB4_init_4", "NB4_uniform_particles"]),
    ("NB4_maxwell2d", check_maxwell_fit, ["NB4_init_1", "NB4_init_2", "NB4_init_3", "NB4_init_4","NB4_uniform_particles"]),
    ("NB4_excellent", check_excellent, []),
]

NB9_cell_checks = [
    ("NB9_E_T", check_E_T, []),
    ("NB9_E_T_2", check_E_T_2, []),
    ("NB9_optimum", check_optimum, ["NB9_E_T", "NB9_E_T_2"]),
]

cell_checks = {
    "NB1": NB1_cell_checks,
    "NB2": NB2_cell_checks,
    "NB3": NB3_cell_checks,
    "NB4": NB4_cell_checks,
    "NB9": NB9_cell_checks,
}

written_checks = {
    "NB2": [
        ("ex-recap-5", check_written_solution),
        ("ex-recap-6", check_written_solution),
        ("ex-brownian-1", check_written_solution),
        ("ex-brownian-3", check_written_solution),
    ],
}



# get command line arguments
args = sys.argv[1:]
if len(args) == 1 and args[0] in cell_checks:
    # Only run checks for the specified notebook
    print(f"Running checks for notebook: {args[0]}")
    for name, test_function, init_tags in cell_checks[args[0]]:
        check_cell(
            name,
            notebook_file_paths[args[0]],
            test_function,
            init_tags=init_tags
        )
else:
    # Run all checks
    for notebook, path in notebook_file_paths.items():
        for name, test_function, init_tags in cell_checks[notebook]:
            check_cell(
                name,
                path,
                test_function,
                init_tags=init_tags
            )

# Check written answers
if len(args) == 1 and args[0] in cell_checks:
    notebooks_to_check = [args[0]]
else:
    notebooks_to_check = list(cell_checks.keys())

for notebook in notebooks_to_check:
    for tag, test_function in written_checks.get(notebook, []):
        check_written_answer(
            tag,
            notebook_file_paths[notebook],
            test_function
        )


# Generate Markdown report
output = Path("codechecks.md")
output.parent.mkdir(parents=True, exist_ok=True)

with output.open("w", encoding="utf-8") as f:
    f.write("# Notebook checks\n\n")
    f.write("| Check | Status | Details |\n")
    f.write("|-------|--------|---------|\n")

    for name, passed, message in results:
        if passed == "REVIEW":
            status = "📝 REVIEW"
        elif passed:
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        details = str(message).replace("|", r"\|").replace("\n", "<br>")
        f.write(f"| {name} | {status} | {details} |\n")
        
