from pathlib import Path
import numpy as np
import jupytext
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt

from NB1 import (
    check_doorlopende_doos,
    check_harde_wanden,
    check_botsingsvoorwaarde,
    check_eindantwoord,
)

from NB2 import (
    check_brownian_distance_histogram_solution,
)


from NB3 import (
    check_tempfun,
    check_const_temp,
)

def get_tagged_cell(notebook_path, tag):
    nb = jupytext.read(notebook_path)

    for cell in nb.cells:
        if cell.cell_type != "code":
            continue

        if tag in cell.metadata.get("tags", []):
            return cell.source

    raise ValueError(f"Geen codecel gevonden met tag {tag!r}")


results = []


def check_cell(
    notebook_path,
    name,
    test_function,
    mode="function",
    variable=None,
    init_tags=None,
):
    try:
        # Shared namespace for all cells in this check
        namespace = {
            "np": np,
            "dt": 0.1,
            "plt": plt,
        }

        # Execute initialization cells first
        for tag in (init_tags or []):
            init_source = get_tagged_cell(notebook_path, tag)
            exec(init_source, namespace)

        # Read the actual exercise cell
        source = get_tagged_cell(notebook_path, name)

        if mode == "source":
            student_object = source

        else:
            # Execute exercise cell in the SAME namespace
            exec(source, namespace)

            if mode == "variable":
                student_object = namespace[variable]

            elif mode == "function":
                # Find functions/classes defined by the exercise cell,
                # not functions from the initialization cells
                import ast

                tree = ast.parse(source)

                defined_names = [
                    node.name
                    for node in tree.body
                    if isinstance(
                        node,
                        (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
                    )
                ]

                objects = [
                    namespace[name]
                    for name in defined_names
                    if callable(namespace.get(name))
                ]

                if len(objects) != 1:
                    raise ValueError(
                        f"Expected one function or class, found {len(objects)}."
                    )

                student_object = objects[0]

            else:
                raise ValueError(f"Unknown check mode: {mode}")

        test_function(student_object)

        results.append((name, True, ""))
        print(f"PASS: {name}")

    except Exception as exc:
        results.append((name, False, str(exc)))
        print(f"FAIL: {name}: {exc}")


# Notebook file paths
notebook_file_paths = {
    "NB1": "simulations/NB1_deeltjesmodel.md",
    "NB2": "simulations/NB2_brownianmotion.md",
    "NB3": "simulations/NB3_druktemp.md",
}

NB1_cell_checks = [
    ("NB1_doorlopendedoos", check_doorlopende_doos, "function", None, []),
    ("NB1_hardewand", check_harde_wanden, "function", None, []),
    ("NB1_botsingsvoorwaarde", check_botsingsvoorwaarde, "function", None, []),
    ("NB1_eindantwoord", check_eindantwoord, "variable", "num_botsingen", []),
]

NB2_cell_checks = [
    ("NB2_brownian_distance_histogram",
     check_brownian_distance_histogram_solution, "source", None, []),
]

NB3_cell_checks = [
    ("NB3_tempfun", check_tempfun, "function", None),
    ("NB3_check_const_temp", check_const_temp, "variable", "temperatures",
        ["NB3_init_1", "NB3_init_2", "NB3_init_3", "NB3_tempfun", ],),
]

cell_checks = {
    "NB1": NB1_cell_checks,
    "NB2": NB2_cell_checks,
    "NB3": NB3_cell_checks,
}

# Run all checks
for notebook, path in notebook_file_paths.items():
    for name, test_function, mode, variable, init_tags in cell_checks[notebook]:
        check_cell(
            path,
            name,
            test_function,
            mode=mode,
            variable=variable,
            init_tags=init_tags,
        )


# Generate Markdown report
output = Path("codechecks.md")
output.parent.mkdir(parents=True, exist_ok=True)

with output.open("w", encoding="utf-8") as f:
    f.write("# Notebook checks\n\n")
    f.write("| Check | Status | Details |\n")
    f.write("|-------|--------|---------|\n")

    for name, passed, message in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        details = str(message).replace("|", r"\|").replace("\n", "<br>")
        f.write(f"| {name} | {status} | {details} |\n")
        
