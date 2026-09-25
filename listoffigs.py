from pathlib import Path
from html import escape
import shutil
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

        while i < len(lines) and lines[i].strip() != "```":
            line = lines[i].strip()

            name_match = NAME.match(line)

            if name_match:
                label = name_match.group(1)

            # Skip directive options
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


def generate_html(figures):
    """Generate the gallery HTML."""

    cards = []

    for figure in figures:

        label = figure["label"] or "⚠ NO LABEL"
        caption = figure["caption"] or "No caption"

        if figure["gallery_image"]:

            image_html = f"""
                <img
                    src="{escape(figure['gallery_image'])}"
                    alt="{escape(caption)}"
                    loading="lazy"
                >
            """

        else:

            image_html = """
                <div class="missing-image">
                    ⚠ Image not found
                </div>
            """

        cards.append(
            f"""
            <figure class="figure-card">

                {image_html}

                <figcaption>

                    <strong>
                        {escape(label)}
                    </strong>

                    <p>
                        {escape(caption)}
                    </p>

                    <small>
                        {escape(str(figure["source"]))}
                    </small>

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

<h1>Figure Gallery</h1>

<p>
    {len(figures)} figures found.
</p>

<div class="gallery">

{''.join(cards)}

</div>

</body>

</html>
"""


def main():

    project_dir = Path.cwd()

    content_dir = project_dir / "content"

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

    for markdown_file in content_dir.rglob("*.md"):
        figures.extend(
            find_figures(markdown_file)
        )

    print(
        f"Found {len(figures)} figures"
    )

    # Copy original images into gallery
    copy_images(
        figures,
        gallery_dir
    )

    # Generate HTML
    html = generate_html(figures)

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