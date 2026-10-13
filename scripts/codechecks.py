from pathlib import Path
import nbformat
import html
import numpy as np
from types import SimpleNamespace
import jupytext 


from NB1 import (
    check_doorlopende_doos,
    check_harde_wanden,
    check_botsingsvoorwaarde,
    check_eindantwoord,
)


def get_tagged_cell(notebook_path, tag):
    nb = jupytext.read(notebook_path)

    for cell in nb.cells:
        if cell.cell_type != "code":
            continue

        if tag in cell.metadata.get("tags", []):
            return cell.source

    raise ValueError(f"Geen codecel gevonden met tag {tag!r}")

# CODE BELOW FOR .IPYNB NOTEBOOKS, NOT FOR .MD FILES
# def get_tagged_cell(notebook_path, tag):
#     nb = nbformat.read(notebook_path, as_version=4)

#     for cell in nb.cells:
#         if tag in cell.metadata.get("tags", []):
#             return cell.source

#     raise ValueError(f"Geen cel gevonden met tag {tag!r}")

results = []


def check_cell(name, notebook_path, test_function, variable=None):

    try:
        # Find the tagged cell
        source = get_tagged_cell(notebook_path, name)

        # Provide dependencies for the student's code
        namespace = {
            "np": np,
            "dt": 0.1,
        }

        # Execute the student's code
        # Syntax errors are now caught by try/except
        exec(source, namespace)

        if variable is not None:
            # Retrieve a variable, e.g. num_botsingen
            student_object = namespace[variable]

        else:
            # Retrieve the function or class defined by the student
            objects = [
                value
                for key, value in namespace.items()
                if callable(value) and not key.startswith("__")
            ]

            if len(objects) != 1:
                raise ValueError(
                    f"Expected one function or class, found {len(objects)}."
                )

            student_object = objects[0]

        # Run the corresponding test from NB1.py
        test_function(student_object)

        results.append((name, True, ""))
        print(f"PASS: {name}")

    except Exception as exc:
        results.append((name, False, str(exc)))
        print(f"FAIL: {name}: {exc}")


# Run all checks
notebook_1 = "simulations/NB1_deeltjesmodel.md"

check_cell("NB1_doorlopendedoos", notebook_1, check_doorlopende_doos)

check_cell("NB1_hardewand", notebook_1, check_harde_wanden)

check_cell("NB1_botsingsvoorwaarde", notebook_1, check_botsingsvoorwaarde)

check_cell("NB1_eindantwoord", notebook_1, check_eindantwoord, variable="num_botsingen")

# results = []        # Store the results of all checks

# # Get python code from tagged cell from the specified notebook file
# source = [
#         # get_tagged_cell("simulations/opdracht.ipynb",  "sol_check_1"), 
#         # get_tagged_cell("simulations/opdracht.ipynb",  "sol_check_2"),
#         get_tagged_cell("simulations/NB1_deeltjesmodel.md", "NB1_doorlopendedoos"),
#         get_tagged_cell("simulations/NB1_deeltjesmodel.md", "NB1_hardewand"),
#         get_tagged_cell("simulations/NB1_deeltjesmodel.md", "NB1_botsingsvoorwaarde"),
#         get_tagged_cell("simulations/NB1_deeltjesmodel.md", "NB1_eindantwoord"),
#         ]


# functions = []

# for sources in source:
#     namespace = {
#     "np": np,
#     "dt": 0.1,
#         }           # Make empty dictionary to hold the namespace after executing the student's code
#     exec(sources, namespace)

#     # Search for the functions defined in the student's code.
#     found_functions = [
#         value
#         for name, value in namespace.items()
#         if callable(value) and not name.startswith("__")
#     ]



#     # Check that there is exactly one function defined in the student's code.
#     if len(found_functions) != 1:
#         raise ValueError(
#             f"Expect only one function, "
#             f"but found {len(found_functions)}."
#         )

#     functions.append(found_functions[0])

# # Use the first (and only) function found in the student's code.
# student_func = functions[0]

# # General function to run a check and store the result in the results list.
# def check(name, func, *args):

#     try:
#         func(*args)             # do the check

#         results.append(
#             (name, True, "")    # if no exception was raised, the check passed
#         )

#         print(f"PASS: {name}")  # else copy error message to results and print FAIL

#     except Exception as exc:

#         # Store the name of the check, a False value indicating failure, and the exception message in the results list.
#         results.append(
#             (name, False, str(exc))
#         )

#         print(f"FAIL: {name}: {exc}")





# ######### CHECK THE SOLUTIONS OF THE TAGGED CELLS #########

# check("NB1_doorlopendedoos", check_doorlopende_doos, functions[0])
# check("NB1_hardewand", check_harde_wanden, functions[1])
# check("NB1_botsingsvoorwaarde", check_botsingsvoorwaarde, functions[2])
# check("NB1_eindantwoord", check_eindantwoord, functions[3])


##### GENERATE MARKDOWN REPORT #####
output = Path("codechecks.md")
output.parent.mkdir(parents=True, exist_ok=True)

with output.open("w") as f:
    f.write("# Notebook checks\n\n")
    f.write("| Check | Status | Details |\n")
    f.write("|-------|--------|---------|\n")

    for name, passed, message in results:
        status = "✅ PASS" if passed else "❌ FAIL"

        # Keep exception messages inside one Markdown table cell
        details = str(message).replace("|", r"\|").replace("\n", "<br>")

        f.write(f"| {name} | {status} | {details} |\n")
