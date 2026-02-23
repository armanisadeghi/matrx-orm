import os
import sys
from git import Repo, GitCommandError, InvalidGitRepositoryError
from matrx_utils import vcprint


def check_git_status(save_direct: bool, python_root: str = "", ts_root: str = "", ignore_path_prefixes: list[str] | None = None) -> bool:
    """
    Check if python_root and ts_root are git repositories with no uncommitted
    changes before allowing a save_direct write that could overwrite live files.

    Falls back to ADMIN_PYTHON_ROOT / ADMIN_TS_ROOT env vars when the caller
    doesn't supply explicit paths (backward-compat).

    Returns True if safe to proceed, exits with code 1 if not.
    """
    python_root = python_root or os.getenv("ADMIN_PYTHON_ROOT", "")
    ts_root = ts_root or os.getenv("ADMIN_TS_ROOT", "")

    roots_to_check = [
        ("Python root", python_root),
        ("TypeScript root", ts_root),
    ]
    has_issues = False

    if not save_direct:
        vcprint(
            "[MATRX ORM GIT CHECKER] save_direct is False - skipping git checks",
            color="green",
        )
        return True

    vcprint("\n[MATRX ORM GIT CHECKER] Checking git repository status...\n", color="yellow")
    vcprint(f"[MATRX ORM GIT CHECKER] Python root:     {python_root}", color="green")
    vcprint(f"[MATRX ORM GIT CHECKER] TypeScript root: {ts_root}", color="green")
    print()

    for root_name, root_path in roots_to_check:
        vcprint(f"\n[MATRX ORM GIT CHECKER] Checking {root_name}...", color="yellow")

        # Skip if path is not set
        if not root_path:
            vcprint(f"- {root_name} path not set", color="yellow")
            continue

        # Check if path exists
        if not os.path.exists(root_path):
            vcprint(f"- {root_name} path '{root_path}' does not exist — skipping git check for this root", color="yellow")
            continue

        try:
            # Try to initialize repo object
            repo = Repo(root_path)
            vcprint("- [MATRX ORM GIT CHECKER] Git repository found! ✓", color="green")
            vcprint("- Checking git status...\n", color="green")

            # Check if there are uncommitted changes
            if repo.is_dirty(untracked_files=True):
                raw_lines = [
                    line
                    for line in repo.git.status("--porcelain").split("\n")
                    if line.strip()
                ]
                # porcelain format: "XY filename" — always 2 status chars + space
                # slice from index 3 on the raw (unstripped) line to get the filename
                changed_files = [line[3:].strip() for line in raw_lines]
                modified_lines = [line.strip() for line in raw_lines]

                # These files are auto-managed and safe to ignore during generation.
                _IGNORABLE_NAMES = {"matrx_orm.yaml", "uv.lock", "poetry.lock", "package-lock.json", "yarn.lock"}
                _ignore_prefixes = [p.lstrip("/") for p in (ignore_path_prefixes or [])]

                def _is_ignorable(filepath: str) -> bool:
                    if os.path.basename(filepath) in _IGNORABLE_NAMES:
                        return True
                    return any(filepath.startswith(prefix) for prefix in _ignore_prefixes)

                non_ignorable = [f for f in changed_files if not _is_ignorable(f)]

                if not non_ignorable:
                    vcprint(
                        f"- Only auto-managed files changed ({', '.join(os.path.basename(f) for f in changed_files)}) — treating as clean ✓",
                        color="green",
                    )
                else:
                    vcprint("- Uncommitted changes detected! Details:\n", color="red")
                    vcprint("  Modified files:", color="red")
                    for line in modified_lines:
                        vcprint(f"    {line}", color="red")
                    has_issues = True
            else:
                vcprint("- No uncommitted changes found ✓", color="green")

        except InvalidGitRepositoryError:
            vcprint("- Not a git repository ✓", color="green")
            vcprint("- Proceeding as regular directory...", color="green")
            continue
        except GitCommandError as e:
            vcprint(f"- Error checking git status: {str(e)}", color="red")
            has_issues = True
        except Exception as e:
            vcprint(f"- Unexpected error: {str(e)}", color="red")
            has_issues = True

    if has_issues:
        vcprint(
            "\n[MATRX ORM GIT CHECKER] Error: Cannot proceed with save_direct=True\n",
            color="red",
        )
        vcprint(
            "[MATRX ORM GIT CHECKER] Your Options:\n --> Option 1: Commit or stash your changes first.\n --> Option 2: Set save_direct=False.\n --> Option 3: Change your environmental variables to point to a different or temporary directory.\n",
            color="red",
        )
        sys.exit(1)
    else:
        vcprint("\n[MATRX ORM GIT CHECKER] All checks passed ✓", color="green")

    return True
