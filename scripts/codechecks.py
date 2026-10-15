from pathlib import Path
import numpy as np
import jupytext

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


def check_cell(notebook_path, name, test_function, variable=None):
    try:
        source = get_tagged_cell(notebook_path, name)

        if variable is None:
            # Exercise 15 checks the source code directly.
            student_object = source
        else:
            namespace = {"np": np, "dt": 0.1}
            exec(source, namespace)
            student_object = namespace[variable]

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

# NB1 checks remain unchanged
NB1_cell_checks = [
    ("NB1_doorlopendedoos", check_doorlopende_doos),
    ("NB1_hardewand", check_harde_wanden),
    ("NB1_botsingsvoorwaarde", check_botsingsvoorwaarde),
    ("NB1_eindantwoord", check_eindantwoord, "num_botsingen"),
]

# Only check exercise 15 for NB2
NB2_cell_checks = [
    ("NB2_brownian_distance_histogram", check_brownian_distance_histogram_solution),
]

NB3_cell_checks = [
    ("NB3_tempfun", check_tempfun),
]

cell_checks = {
    "NB1": NB1_cell_checks,
    "NB2": NB2_cell_checks,
    "NB3": NB3_cell_checks,
}

# Run all checks
for notebook, path in notebook_file_paths.items():
    for name, test_function, *args in cell_checks[notebook]:
        check_cell(path, name, test_function, *args)


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
        
