"""Generate gitlog.md with conservative branch attribution.

Git commits do not record their original branch. A branch is inferred only
when exactly one currently existing branch contains the commit.
"""

import csv
import fnmatch
import json
import subprocess
from pathlib import Path

CSV_FILE = Path('allowed_users.csv')
OUTPUT_FILE = Path('gitlog.md')


def git(*args):
    return subprocess.run(['git', *args], capture_output=True, text=True,
                          check=True).stdout


def load_permissions():
    permissions = {}
    with CSV_FILE.open(newline='', encoding='utf-8-sig') as handle:
        for row in csv.DictReader(handle):
            username = row['username'].strip().casefold()
            patterns = json.loads(row['branches'])
            if not isinstance(patterns, list) or not all(isinstance(p, str) for p in patterns):
                raise ValueError(f'Invalid branches for {username}: expected JSON array')
            permissions[username] = patterns
    return permissions

def list_branches():
    # Prefer remote branches; local checkout branches often duplicate them.
    remote_refs = git('for-each-ref', '--format=%(refname)', 'refs/remotes').splitlines()
    branches = {}
    for ref in remote_refs:
        if ref.endswith('/HEAD'):
            continue
        name = ref.removeprefix('refs/remotes/')
        if '/' not in name:
            continue
        remote, short_name = name.split('/', 1)
        if remote == 'origin':
            branches[short_name] = ref
    # Fallback for repositories without origin remote refs.
    if not branches:
        for ref in git('for-each-ref', '--format=%(refname)', 'refs/heads').splitlines():
            branches[ref.removeprefix('refs/heads/')] = ref
    return branches

def get_commits():
    output = git('log', '--all', '--date=short',
                 '--pretty=format:%ad%x1f%H%x1f%an%x1e')
    commits = []
    for record in output.split('\x1e'):
        record = record.strip('\r\n')
        if not record:
            continue
        fields = record.split('\x1f')
        if len(fields) != 3:
            raise ValueError(f'Unexpected git log record: {record!r}')
        date, sha, author = fields
        commits.append((date, sha, author))
    return commits


def branch_memberships(branches):
    membership = {}
    for name, ref in branches.items():
        for sha in git('rev-list', ref).splitlines():
            membership.setdefault(sha, set()).add(name)
    return membership

def escape_md(value):
    return str(value).replace('|', '\\|').replace('\n', ' ')


def generate_markdown():
    permissions = load_permissions()
    commits = get_commits()
    branches = list_branches()
    memberships = branch_memberships(branches)

    lines = [
        '| Commit date | Commit ID | Committed user | Branch | Allowed |',
        '|---|---|---|---|---|',
    ]
    known = ambiguous = 0
    for date, sha, author in commits:
        candidates = memberships.get(sha, set())
        if len(candidates) == 1:
            branch = next(iter(candidates))
            # A unique containing branch is only an inference, not proof.
            allowed = any(fnmatch.fnmatchcase(branch, pattern)
                          for pattern in permissions.get(author.strip().casefold(), []))
            status = 'Yes*' if allowed else 'No*'
            known += 1
        else:
            branch = 'unknown'
            status = 'Unknown'
            ambiguous += 1
        lines.append(f'| {escape_md(date)} | `{sha[:12]}` | {escape_md(author)} '
                     f'| {escape_md(branch)} | {status} |')
        
    lines.extend([
        '',
        '*`Yes*` / `No*` is a **provisional** permission check: the branch is inferred '
        'from current branch reachability, not proven as the original branch. '
        '`Unknown` means the original branch cannot be determined from the available refs.*',
    ])
    OUTPUT_FILE.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'Report generated: {OUTPUT_FILE} ({len(commits)} commits, '
          f'{known} inferred, {ambiguous} unknown; {len(branches)} branches)')


if __name__ == '__main__':
    generate_markdown()
