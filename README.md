# mvvid, A Utility Script for Easily Managing Content for PLEX Media Server

## Overview

After adding new content to your PLEX media server, the file(s) may not be in the
proper directory, and even if they are, you need to have PLEX scan the directories
to become aware of the new content.

This script will easily move any content for you to the appropriate directory &
force a refresh of the metadata so that you can view your new content.

This script only works on Linux.

## Requirements

There are some group permissions that do need to be assigned to the user so that
they can move files to the PLEX media server directory.

Also, there are some additional python packages that will need to be installed for
this script to run.

### List of required python packages

1. click
2. rich

## Running the Script

To see a list of all available options, run:

```bash
mvvid --help
```
