from pathlib import Path
import re


def check_written_solution(notebook_path, solution_label):

    content = Path(notebook_path).read_text(encoding="utf-8")

    pattern = (
        r"^```\{solution\}[ \t]+"
        + re.escape(solution_label)
        + r"[ \t]*\r?\n"
        + r"(.*?)"
        + r"^```[ \t]*$"
    )

    match = re.search(
        pattern,
        content,
        re.DOTALL | re.MULTILINE
    )

    if match is None:
        raise ValueError(
            f"Solution '{solution_label}' niet gevonden"
        )

    answer = match.group(1)

    if not answer.strip():
        raise ValueError(
            f"Solution '{solution_label}' is leeg"
        )

    return answer