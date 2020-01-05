#!/usr/bin/env python3

import click
from fnmatch import fnmatch
import getpass
import os
from pathlib import Path
import shutil
import sys
from typing import List

plex_dir = Path("/var/lib/plexmediaserver/Library/")
curr_dir = Path.cwd()


class InvalidUserError(Exception):
    """Raise this exception if script is run as any user other that root user.
    """

    pass


def only_as_root() -> bool:
    """Make sure that the only user running this script is root user.
    Otherwise raise InvalidUserError exception.
    """
    current_user = getpass.getuser()
    if current_user != "root":
        raise InvalidUserError("Script can only be run as root user!")
    return True


def to_target(target_option: bool) -> Path:
    """Return Path to target directory based on target option.
    """
    target_dir = plex_dir / ("TV_Shows" if target_option else "Movies")
    click.echo(f"Destination directory: {target_dir}")
    return target_dir


def from_source(match_string: str) -> List[Path]:
    """Return list of file(s)/directory(s) in current directory matching given
    pattern.
    """
    return [f for f in sorted(curr_dir.iterdir()) if fnmatch(f.name, match_string)]


def get_confirmation(confirm: bool) -> bool:
    """Get user confirmation. If user does not confirm, then exit.
    """
    if not confirm:
        response = input("Do you wish to continue? (Y/N) ")
    if confirm or response.lower().startswith("y"):
        return True
    click.echo("Canceling move at user request. Exiting . . .")
    sys.exit(1)


def change_owner(target: Path) -> None:
    """Change owner to plex:plex for file/directory.
    """
    if target.is_dir():
        for each_file in target.iterdir():
            shutil.chown(each_file, "plex", "plex")
    # Change owner whether file or directory
    shutil.chown(target, "plex", "plex")
    click.echo(f"{target} owner changed to plex:plex")


def move_source_to_target(source_list: List[Path], target: Path) -> None:
    """Move source directory/file to target directory.
    """
    for each in source_list:
        click.echo(f"Moving {each.name} -> {target}")
        target_name = target / each.name
        if each.is_dir():
            shutil.copytree(each, target_name)
            shutil.rmtree(each)
        else:
            shutil.copy(each, target_name)
            each.unlink()
        change_owner(target_name)
    click.echo(f"Total of {len(source_list)} directory(s)/file(s) moved.")


def refresh_plex_metadata() -> None:
    """Refresh PLEX metadata so that new items will appear in menu.
    """
    click.echo("Refreshing PLEX metadata . . .")
    os.system("sudo su - plex -c ./plex_analyze.sh")


@click.command()
@click.option("--tv/--movie", "target", required=True, help="Content type")
@click.option(
    "--match",
    default="*",
    required=True,
    help="Regex pattern of file(s)/directory(s) to move",
)
@click.option(
    "-y", "-Y", "confirmation", is_flag=True, help="Confirm move without prompt"
)
def main(target, match, confirmation) -> None:
    """Copies directory(s) containing videos and/or video files to PLEX directory
    and refresh PLEX metadata.

    Because this script moves file(s)/directory(s) owned by different users,
    it can only be run as root.
    """
    if only_as_root():
        target_dir = to_target(target)
        source_list = from_source(match)
        click.echo(
            f"The following directory(s)/file(s) will be moved to {target_dir}:"
        )
        click.echo("\n".join(f"\t{f.name}" for f in source_list))
        if get_confirmation(confirmation):
            move_source_to_target(source_list, target_dir)
            refresh_plex_metadata()
        click.echo("Exiting . . .")


if __name__ == "__main__":
    main()
