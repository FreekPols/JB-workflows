    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True
    )

    commits = []

    for entry in result.stdout.strip("\x1e\n").split("\x1e"):
        if not entry.strip():
            continue

        parts = entry.strip().split("\x1f")

        if len(parts) != 3:
            continue

        date, commit_id, username = parts

        commits.append({
            "date": date,
            "id": commit_id,
            "username": username
        })

    print(f"Found {len(commits)} commits")
    return commits


def get_branches(commit_id):
    result = subprocess.run(
        [
            "git", "branch",
            "-a", "--contains", commit_id,
            "--format=%(refname:short)"
        ],
        capture_output=True,
        text=True,
        check=True
    )

    branches = []

    for branch in result.stdout.splitlines():
        branch = branch.strip()

        if branch.startswith("origin/"):
            branch = branch[len("origin/"):]

        if branch and branch not in branches:
            branches.append(branch)

    return branches


def is_allowed(username, branch, permissions):
    allowed_branches = permissions.get(
        username.strip().lower(), []
    )

    return any(
        fnmatch.fnmatchcase(branch, pattern)
        for pattern in allowed_branches
    )


def generate_markdown():
    permissions = load_permissions()
    commits = get_git_log()

    lines = [
        "| Commit date | Commit ID | Committed user | Branch | Allowed |",
        "|---|---|---|---|---|"
    ]

    for commit in commits:
        branches = get_branches(commit["id"])

        if not branches:
            branches = ["unknown"]

        for branch in branches:
            allowed = is_allowed(
                commit["username"],
                branch,
                permissions
            )

            status = "Yes" if allowed else "No"

            lines.append(
                f"| {commit['date']} "
                f"| `{commit['id'][:12]}` "
                f"| {commit['username']} "
                f"| {branch} "
                f"| {status} |"
            )

    Path(OUTPUT_FILE).write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8"
    )

    print(f"Report generated: {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_markdown()
