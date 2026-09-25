from pathlib import Path
from html import escape
import re


FIGURE_START = re.compile(r"^```\{figure\}\s+(.+?)\s*$")
NAME = re.compile(r"^:name:\s*(.+?)\s*$")


def find_figures(markdown_file: Path):
    """Return all MyST figure directives in a Markdown file."""

    lines = markdown_file.read_text(encoding="utf-8").splitlines()
    figures = []

    i = 0

    while i < len(lines):
        match = FIGURE_START.match(lines[i].strip())

        if not match:
            i += 1
            continue

        image_path = match.group(1)
        label = ""
        caption_lines = []

        i += 1

        # Read everything until closing ```
        while i < len(lines) and lines[i].strip() != "```":
            line = lines[i].strip()

            name_match = NAME.match(line)

            if name_match:
                label = name_match.group(1)

            # Ignore directive options such as :width:, :align:, etc.
            elif line.startswith(":") and line.endswith(":"):
                pass

            elif not line.startswith(":"):
                caption_lines.append(lines[i].strip())

            i += 1

        caption = " ".join(
            line for line in caption_lines if line
        )

        figures.append(
            {
                "image": image_path,
                "label": label,
                "caption": caption,
                "source": markdown_file,
            }
        )

        i += 1

    return figures


def generate_html(figures, project_dir: Path):
    """Generate a single HTML figure gallery."""

    cards = []

    for figure in figures:
        source = figure["source"]
        image = figure["image"]

        # Resolve image relative to the Markdown file
        absolute_image = (source.parent / image).resolve()

        try:
            relative_image = absolute_image.relative_to(project_dir)
        except ValueError:
            relative_image = absolute_image

        cards.append(
            f"""
            <figure class="figure-card">
                <img
                    src="../../{escape(str(relative_image))}"
                    alt="{escape(figure['caption'])}"
                    loading="lazy"
                >
                <figcaption>
                    <strong>{escape(figure['label'])}</strong>
                    <p>{escape(figure['caption'])}</p>
                    <small>{escape(str(source.relative_to(project_dir)))}</small>
                </figcaption>
            </figure>
            """
        )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Figure Gallery</title>

<style>
body {{
    font-family: system-ui, sans-serif;
    max-width: 1600px;
    margin: 40px auto;
    padding: 0 30px;
}}

.gallery {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 30px;
}}

.figure-card {{
    margin: 0;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 15px;
}}

.figure-card img {{
    width: 100%;
    height: 250px;
    object-fit: contain;
}}

figcaption {{
    margin-top: 15px;
}}

figcaption p {{
    margin: 8px 0;
}}

small {{
    color: #666;
}}
</style>
</head>

<body>

<h1>Figure Gallery</h1>

<p>{len(figures)} figures found.</p>

<div class="gallery">
{''.join(cards)}
</div>

</body>
</html>
"""


def main():
    project_dir = Path.cwd()
    content_dir = project_dir / "content"
    output_dir = project_dir / "_build" / "html"

    figures = []

    for markdown_file in content_dir.rglob("*.md"):
        figures.extend(find_figures(markdown_file))

    print(f"Found {len(figures)} figures")

    for figure in figures:
        print(
            f"  {figure['label'] or '[no label]'} "
            f"- {figure['caption']}"
        )

    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "figure-gallery.html"

    output_file.write_text(
        generate_html(figures, project_dir),
        encoding="utf-8",
    )

    print(f"Gallery written to {output_file}")


if __name__ == "__main__":
    main()