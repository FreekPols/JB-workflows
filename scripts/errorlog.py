from pathlib import Path
from html import escape


log_file = Path("build.log")
output_file = Path("_build/html/errorlog.html")

# Make sure the output directory exists
output_file.parent.mkdir(parents=True, exist_ok=True)


# -------------------------
# Read MyST build log
# -------------------------

if not log_file.exists():
    raise FileNotFoundError("build.log was not found")

text = log_file.read_text(
    encoding="utf-8",
    errors="replace"
)


# -------------------------
# Collect errors and warnings
# -------------------------

errors = []
warnings = []

for line in text.splitlines():
    line = line.strip()

    if "⛔️" in line or "⛔" in line:
        errors.append(line)

    elif "⚠️" in line or "⚠" in line:
        warnings.append(line)


# -------------------------
# Generate HTML entries
# -------------------------

error_items = "".join(
    f"<li>{escape(error)}</li>"
    for error in errors
)

warning_items = "".join(
    f"<li>{escape(warning)}</li>"
    for warning in warnings
)


# -------------------------
# Generate HTML page
# -------------------------

html = f"""<!doctype html>
<html lang="en">

<head>
<meta charset="utf-8">
<title>MyST Build Report</title>

<style>

body {{
    font-family: system-ui, sans-serif;
    max-width: 1200px;
    margin: 40px auto;
    padding: 0 30px;
}}

h1 {{
    margin-bottom: 5px;
}}

.summary {{
    margin: 25px 0;
    padding: 15px;
    background: #f5f5f5;
    border-radius: 8px;
}}

li {{
    margin-bottom: 10px;
    font-family: monospace;
}}

</style>
</head>

<body>

<h1>MyST Build Report</h1>

<div class="summary">
    <strong>{len(errors)} errors</strong>
    and
    <strong>{len(warnings)} warnings</strong>
    found.
</div>

<h2>⛔ Errors</h2>

<ul>
    {error_items if errors else "<li>✅ No errors found.</li>"}
</ul>

<h2>⚠️ Warnings</h2>

<ul>
    {warning_items if warnings else "<li>✅ No warnings found.</li>"}
</ul>

</body>
</html>
"""


# -------------------------
# Write report
# -------------------------

output_file.write_text(
    html,
    encoding="utf-8"
)

print(
    f"Build report written to {output_file} "
    f"({len(errors)} errors, {len(warnings)} warnings)"
)