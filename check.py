from pathlib import Path
import sys

def check_header_labels(path: Path) -> list[str]:
    """Check whether every Markdown header has a MyST label."""

    lines = path.read_text(encoding="utf-8").splitlines()
    errors = []

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Markdown header: #, ##, ###, etc.
        if stripped.startswith("#"):

            # Ignore things that start with # but aren't headers
            if not stripped.startswith(("# ", "## ", "### ", "#### ", "##### ", "###### ")):
                continue

            line_number = i + 1

            # First line can never have a preceding label
            if i == 0:
                errors.append(
                    f"{path}:{line_number}: "
                    f"header has no label: {stripped}"
                )
                continue

            previous_line = lines[i - 1].strip()

            # A MyST label looks like: (some_label)=
            has_label = (
                previous_line.startswith("(")
                and previous_line.endswith(")=")
            )

            if not has_label:
                errors.append(
                    f"{path}:{line_number}: "
                    f"header has no label: {stripped}"
                )

    return errors

def check_file(path: Path) -> list[str]:
    """Check whether every {figure} directive has a :name: label."""

    lines = path.read_text(encoding="utf-8").splitlines()
    errors = []

    inside_figure = False
    figure_end = None
    figure_start_line = None
    has_name = False

    for line_number, line in enumerate(lines, start=1):

        # Start of a figure directive
        if line.strip().startswith(("```{figure}", ":::{figure}")):
            inside_figure = True
            figure_end = "```" if line.strip().startswith("```{figure}") else ":::"
            figure_start_line = line_number
            has_name = False

        # While inside the figure, look for :name:
        elif inside_figure and line.strip().startswith((":name:", ":label:")):
            has_name = True

        # End of the figure directive
        elif inside_figure and line.strip() == figure_end:
            if not has_name:
                errors.append(
                    f"{path}:{figure_start_line}: "
                    "figure directive has no :name: label"
                )

            inside_figure = False

    return errors


def main():
    project_dir = Path(__file__).resolve().parent.parent

    book_dir = project_dir / "content"

    markdown_files = book_dir.rglob("*.md")

    errors = []

    for path in markdown_files:
        errors.extend(check_header_labels(path))
        # print(path)
        errors.extend(check_file(path))

    if errors:
        print("Some checks failed:\n")

        for error in errors:
            print(f"  ❌ {error}")

        # sys.exit(1)
    if not errors:
        print("✅ All checks passed.")


if __name__ == "__main__":
    main()