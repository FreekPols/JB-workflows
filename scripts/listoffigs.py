from pathlib import Path
from html import escape
import shutil
import re


FIGURE_START = re.compile(r"^(```|:::)\{figure\}\s+(.+?)\s*$")
LABEL = re.compile(r"^:(?:name|label):\s*(.+?)\s*$")
ALT_TEXT = re.compile(r"^:alt:\s*(.*?)\s*$")

def generate_html(figures, project_dir: Path):
    """Generate HTML with a figure overview table and gallery."""

    table_rows = []
    cards = []

    for figure in figures:
        label = figure["label"] or "⚠ NO LABEL"
        caption = figure["caption"] or "No caption"
        alt_text = figure["alt_text"] or "No alt text"

        # Show source relative to repository root
        try:
            source = figure["source"].relative_to(project_dir)
        except ValueError:
            source = figure["source"]

        # Original filename/path from the MyST directive
        figure_name = figure["image"]

        # -------------------------
        # Table
        # -------------------------

        alt_status = (
            "✓ Present"
            if figure["has_alt_text"]
            else "⚠ Missing"
        )

        table_rows.append(
            f"""
            <tr>
                <td>{escape(figure_name)}</td>
                <td>{escape(caption)}</td>
                <td><code>{escape(label)}</code></td>
                <td>{escape(alt_text)}</td>
                <td>{alt_status}</td>
                <td><code>{escape(str(source))}</code></td>
            </tr>
            """
        )

        

        # -------------------------
        # Gallery
        # -------------------------

        if figure["gallery_image"]:
            image_path = escape(figure["gallery_image"])

            image_html = f"""
                <a href="{image_path}" target="_blank">
                            <img
                                src="{image_path}"
                                alt="{escape(figure['alt_text'])}"
                                loading="lazy"
                            >
                        </a>
            """
        else:
            image_html = """
                <div class="missing-image">
                    ⚠ Image not found
                </div>
            """

            alt_info = (
                    f'<p class="alt-text">'
                    f'<strong>Alt text:</strong> {escape(alt_text)}'
                    f'</p>'
                    if figure["has_alt_text"]
                    else '<p class="alt-warning">'
                        '⚠ Missing alt text'
                        '</p>'
                )

            cards.append(
                f"""
                <figure class="figure-card">

                    {image_html}

                    <figcaption>
                        <strong>{escape(label)}</strong>

                        <p>{escape(caption)}</p>

                        {alt_info}

                        <small>
                            {escape(str(source))}
                        </small>
                    </figcaption>

                </figure>
                """
            )

    return f"""<!doctype html>

<html lang="en">

<head>

<meta charset="utf-8">

<title>Figure Report</title>

<style>

body {{
    font-family: system-ui, sans-serif;
    max-width: 1600px;
    margin: 40px auto;
    padding: 0 30px;
}}

h1 {{
    margin-bottom: 5px;
}}

h2 {{
    margin-top: 50px;
}}

/* -------------------------
   Overview table
   ------------------------- */

table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 25px;
}}

th,
td {{
    text-align: left;
    padding: 10px;
    border-bottom: 1px solid #ddd;
    vertical-align: top;
}}

th {{
    background: #f5f5f5;
}}

tr:hover {{
    background: #fafafa;
}}

code {{
    white-space: nowrap;
}}

/* -------------------------
   Gallery
   ------------------------- */

.gallery {{
    display: grid;
    grid-template-columns:
        repeat(auto-fill, minmax(300px, 1fr));
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

.missing-image {{
    height: 250px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #eee;
}}

</style>

</head>

<body>

<h1>Figure Report</h1>

<p>
    {len(figures)} figures found in this book.
</p>


<h2>Figure overview</h2>

<table>

<thead>
<tr>
    <th>Figure name</th>
    <th>Caption</th>
    <th>Label</th>
    <th>Alt text</th>
    <th>Alt status</th>
    <th>Source</th>
</tr>
</thead>

<tbody>

{''.join(table_rows)}

</tbody>

</table>


<h2>Figure gallery</h2>

<div class="gallery">

{''.join(cards)}

</div>

</body>

</html>
"""




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

        fence = match.group(1)
        image_path = match.group(2)

        label = ""
        alt_text = ""
        caption_lines = []

        i += 1

        while i < len(lines) and lines[i].strip() != fence:
            line = lines[i].strip()

            label_match = LABEL.match(line)
            alt_match = ALT_TEXT.match(line)

            if label_match:
                label = label_match.group(1)

            elif alt_match:
                alt_text = alt_match.group(1)

            # Skip other directive options
            elif line.startswith(":"):
                pass

            elif line:
                caption_lines.append(line)

            i += 1

        caption = " ".join(caption_lines)

        figures.append(
            {
                "image": image_path,
                "label": label,
                "caption": caption,
                "alt_text": alt_text,
                "has_alt_text": bool(alt_text.strip()),
                "source": markdown_file,
            }
        )

        i += 1

    return figures



def copy_images(figures, gallery_dir: Path):
    """Copy all figure images into the gallery."""

    images_dir = gallery_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    for number, figure in enumerate(figures, start=1):

        # Image paths in MyST are relative to the Markdown file
        source_image = (
            figure["source"].parent / figure["image"]
        ).resolve()

        if not source_image.exists():
            print(
                f"⚠ Image not found: "
                f"{figure['image']} "
                f"(referenced from {figure['source']})"
            )

            figure["gallery_image"] = None
            continue

        # Keep original extension (.png, .svg, .jpg, ...)
        extension = source_image.suffix

        filename = f"figure-{number:03d}{extension}"

        destination = images_dir / filename

        shutil.copy2(source_image, destination)

        # Path as seen from index.html
        figure["gallery_image"] = f"images/{filename}"

        print(
            f"  Copied {source_image} "
            f"-> {destination}"
        )


def find_markdown_files(project_dir: Path):
    """Find Markdown source files in the project."""

    excluded_dirs = {
        ".git",
        ".github",
        ".jb-workflows",
        "_build",
        "_checks",
        "node_modules",
        ".venv",
        "venv",
    }

    markdown_files = []

    for markdown_file in project_dir.rglob("*.md"):
        relative_path = markdown_file.relative_to(project_dir)

        # Ignore files inside generated/system directories
        if any(part in excluded_dirs for part in relative_path.parts):
            continue

        markdown_files.append(markdown_file)

    return markdown_files

def main():

    project_dir = Path.cwd()

    gallery_dir = (
        project_dir
        / "_build"
        / "html"
        / "figure-gallery"
    )

    gallery_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    figures = []

    for markdown_file in find_markdown_files(project_dir):
        figures.extend(
            find_figures(markdown_file)
        )

    print(
        f"Found {len(figures)} figures"
    )

    copy_images(
        figures,
        gallery_dir
    )

    html = generate_html(figures, project_dir)

    output_file = (
        gallery_dir
        / "index.html"
    )

    output_file.write_text(
        html,
        encoding="utf-8"
    )

    print(
        f"Gallery written to {output_file}"
    )
    


if __name__ == "__main__":
    main()