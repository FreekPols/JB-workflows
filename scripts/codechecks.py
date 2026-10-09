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
)


def get_tagged_cell(notebook_path, tag):
    nb = jupytext.read(notebook_path)

    for cell in nb.cells:
        if cell.cell_type != "code":
            continue

        if tag in cell.metadata.get("tags", []):
            return cell.source

    raise ValueError(f"Geen codecel gevonden met tag {tag!r}")

# def get_tagged_cell(notebook_path, tag):
#     nb = nbformat.read(notebook_path, as_version=4)

#     for cell in nb.cells:
#         if tag in cell.metadata.get("tags", []):
#             return cell.source

#     raise ValueError(f"Geen cel gevonden met tag {tag!r}")

results = []        # Store the results of all checks

# Get python code from tagged cell from the specified notebook file
source = [
        # get_tagged_cell("simulations/opdracht.ipynb",  "sol_check_1"), 
        # get_tagged_cell("simulations/opdracht.ipynb",  "sol_check_2"),
        get_tagged_cell("simulations/NB1_deeltjesmodel.md",  "NB1_doorlopendedoos"),
        get_tagged_cell("simulations/NB1_deeltjesmodel.md",  "NB1_hardewand"),
        get_tagged_cell("simulations/NB1_deeltjesmodel.md", "NB1_botsingsvoorwaarde"),
        ]


functions = []

for sources in source:
    namespace = {}              # Make empty dictionary to hold the namespace after executing the student's code
    exec(sources, namespace)

    # Search for the functions defined in the student's code.
    found_functions = [
        value
        for name, value in namespace.items()
        if callable(value) and not name.startswith("__")
    ]



    # Check that there is exactly one function defined in the student's code.
    if len(found_functions) != 1:
        raise ValueError(
            f"Expect only one function, "
            f"but found {len(found_functions)}."
        )

    functions.append(found_functions[0])

# Use the first (and only) function found in the student's code.
student_func = functions[0]

# General function to run a check and store the result in the results list.
def check(name, func, *args):

    try:
        func(*args)             # do the check

        results.append(
            (name, True, "")    # if no exception was raised, the check passed
        )

        print(f"PASS: {name}")  # else copy error message to results and print FAIL

    except Exception as exc:

        # Store the name of the check, a False value indicating failure, and the exception message in the results list.
        results.append(
            (name, False, str(exc))
        )

        print(f"FAIL: {name}: {exc}")





######### CHECK THE SOLUTIONS OF THE TAGGED CELLS #########

check("NB1_doorlopendedoos", check_doorlopende_doos, functions[0])
check("NB1_hardewand", check_harde_wanden, functions[1])
# check("NB1_botsingsvoorwaarde", check_botsingsvoorwaarde, functions[2])



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


##### GENERARTE HTML REPORT #####
# output = Path("_checks/checks.html")
# output.parent.mkdir(parents=True, exist_ok=True)

# rows = []

# for name, passed, message in results:
#     status = "✅ PASS" if passed else "❌ FAIL"

#     rows.append(f"""
#         <tr>
#             <td>{html.escape(name)}</td>
#             <td>{status}</td>
#             <td>{html.escape(message)}</td>
#         </tr>
#     """)

# output.write_text(
#     f"""<!DOCTYPE html>
# <html lang="nl">
# <head>
#     <meta charset="utf-8">
#     <title>Notebook checks</title>
#     <style>
#         body {{
#             font-family: system-ui, sans-serif;
#             max-width: 1000px;
#             margin: 40px auto;
#             padding: 0 20px;
#         }}
#         table {{
#             border-collapse: collapse;
#             width: 100%;
#         }}
#         th, td {{
#             text-align: left;
#             padding: 10px;
#             border-bottom: 1px solid #ddd;
#         }}
#     </style>
# </head>
# <body>
#     <h1>Notebook checks</h1>
#     <table>
#         <thead>
#             <tr>
#                 <th>Check</th>
#                 <th>Status</th>
#                 <th>Details</th>
#             </tr>
#         </thead>
#         <tbody>
#             {''.join(rows)}
#         </tbody>
#     </table>
# </body>
# </html>
# """,
#     encoding="utf-8",
# )