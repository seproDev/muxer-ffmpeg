from __future__ import annotations

import os
import subprocess
import tomllib
from pathlib import Path


def _pyproject_version() -> str:
    with Path("pyproject.toml").open("rb") as pyproject:
        project = tomllib.load(pyproject)["project"]

    version = project["version"]
    if not isinstance(version, str):
        msg = "project.version must be a string"
        raise SystemExit(msg)
    return version


def _git_output(*args: str, check: bool = True) -> str:
    completed = subprocess.run(
        ["git", *args],
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    return completed.stdout.strip()


def main() -> None:
    version = _pyproject_version()
    tag_name = f"v{version}"
    tag_sha = _git_output("rev-list", "-n", "1", tag_name, check=False)
    if tag_sha:
        msg = f"{tag_name} already exists at {tag_sha}"
        raise SystemExit(msg)

    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with Path(output_path).open("a", encoding="utf-8") as output:
            output.write(f"package_version={version}\n")
            output.write(f"tag_name={tag_name}\n")


if __name__ == "__main__":
    main()
