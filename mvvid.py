#!/usr/bin/env python3

import click
from fnmatch import fnmatch
import getpass
import os
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.theme import Theme
import shutil
import sys
from typing import List

plex_library_dir = Path("/var/lib/plexmediaserver/Library/")
plex_exec_dir = Path("/usr/lib/plexmediaserver")
current_dir = Path.cwd()
custom_theme = Theme(
    {
        "fail": "bold white on red",
        "info": "bold white on blue",
        "low_info": "blue",
        "success": "bold white on green",
        "warn": "bold white on yellow",
    }
)
console = Console(style="bold white", theme=custom_theme)


class InvalidDirectoryError(Exception):
    """Raise this exception if script is run in any other directory than Videos."""

    pass


class InvalidUserError(Exception):
    """Raise this exception if script is run as any user other that root user."""

    pass


def verify_current_directory() -> bool:
    """Make sure that this script is only being run from the Videos directory."""
    if current_dir.name != "Videos":
        raise InvalidDirectoryError(f"No videos found in {current_dir}!")
    return True


def only_as_root() -> bool:
    """Make sure that the only user running this script is root user.
    Otherwise raise InvalidUserError exception.
    """
    current_user = getpass.getuser()
    if current_user != "root":
        raise InvalidUserError("Script can only be run as root user!")
    return True


def to_target(target_option: bool) -> Path:
    """Return Path to target directory based on target option."""
    target_dir = plex_library_dir / ("TV_Shows" if target_option else "Movies")
    console.print("Destination directory: " + f"[success]{target_dir}")
    return target_dir


def from_source(match_string: str) -> List[Path]:
    """Return list of file(s)/directory(s) in current directory matching given
    pattern.
    """
    return [
        f
        for f in sorted(current_dir.iterdir())
        if f.is_symlink() is False and fnmatch(f.name, match_string)
    ]


def get_confirmation(confirm: bool) -> bool:
    """Get user confirmation. If user does not confirm, then exit."""
    if confirm:
        response = input("Do you wish to continue? (Y/N) ")
    if not confirm or response.lower().startswith("y"):
        return True
    console.print(
        ":cross_mark: Canceling move at user request. Exiting . . .", style="fail"
    )
    sys.exit(1)


def change_owner(target: Path) -> None:
    """Change owner to plex:plex for file/directory."""
    if target.is_dir():
        for each_file in target.iterdir():
            shutil.chown(each_file, "plex", "plex")
    # Change owner whether file or directory
    shutil.chown(target, "plex", "plex")
    console.print(
        "  \u2705 owner changed to plex:plex",
        style="low_info",
    )


def move_source_to_target(source_list: List[Path], target: Path) -> None:
    """Move source directory/file to target directory."""
    for n, each in enumerate(source_list, 1):
        console.print(
            f":hourglass_not_done: Moving file/directory {n}/{len(source_list)}: "
            + f"[info]{each.name}"
        )
        target_name = target / each.name
        try:
            if each.is_dir():
                shutil.copytree(each, target_name)
                shutil.rmtree(each)
            else:
                shutil.copy(each, target_name)
                each.unlink()
            change_owner(target_name)
        except FileExistsError:
            console.print(
                f":warning: {each.name} ALREADY EXISTS! Skipping . . .",
                style="warn",
            )
    console.print(
        f"Total of {len(source_list)} directory(s)[info]/file(s) moved.",
        style="info",
    )


def build_table(
    content_list: List[str], target_path: Path, tv_flag: bool
) -> Table:
    """Gather all elements for returning a table containing content to be moved."""
    table = Table(
        title=":information: The following directory(s)[default]/file(s) will be "
        + f"moved to [info]{target_path}[/]:"
    )
    table.add_column("Type", style="low_info")
    content = "TV Show" if tv_flag else "Movie"
    table.add_column(f"{content} Name", justify="center", style="low_info")
    icon = ":television:" if tv_flag else ":clapper_board:"
    for f in content_list:
        table.add_row(icon, f.name, style="low_info")
    return table


def refresh_plex_metadata(target: bool) -> None:
    """Refresh PLEX metadata so that new items will appear in menu."""
    content_label, library_section, icon = (
        ("TV_Shows", 4, ":television: ")
        if target
        else ("Movies", 3, ":clapper_board: ")
    )
    console.print("Refreshing PLEX metadata . . .", style="info")
    os.system(
        f"sudo su - plex -c '{plex_exec_dir}/Plex\ Media\ Scanner -srp "
        + f"--section {library_section}'"
    )
    console.print(
        f"{icon} {content_label} directory refresh complete", style="success"
    )


@click.command()
@click.option(
    "--tv/--movie",
    "target",
    required=True,
    is_flag=True,
    default=True,
    help="Content type, either 'TV show' or 'movie'",
)
@click.option(
    "--match",
    default="*",
    help="Regex pattern of file(s)/directory(s) to move",
)
@click.option(
    "-c",
    "--confirm",
    "confirmation",
    is_flag=True,
    default=False,
    help="Request prompt for confirmation before moving",
)
@click.option(
    "--refresh-only",
    is_flag=True,
    default=False,
    help="Only refresh metadata",
)
def main(target: bool, match: str, confirmation: bool, refresh_only: bool) -> None:
    """Copies directory(s) containing videos and/or video files to PLEX directory
    and refresh PLEX metadata.

    Because this script moves file(s)/directory(s) owned by different users,
    it can only be run as root. Also, it should only ever be run from the Videos
    directory.
    """
    if verify_current_directory() and only_as_root():
        if refresh_only:
            refresh_plex_metadata(target)
            sys.exit(0)
        target_dir = to_target(target)
        source_list = from_source(match)
        console.print(build_table(source_list, target_dir, target))
        if get_confirmation(confirmation):
            move_source_to_target(source_list, target_dir)
            refresh_plex_metadata(target)
        console.print(
            ":checkered_flag: :trophy: Exiting :trophy: :checkered_flag:",
            style="success",
        )


if __name__ == "__main__":
    main()
