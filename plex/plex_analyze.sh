#!/bin/bash

# Used to periodically scan the plex directory & refresh metadata

# Use following command to get source directory numbers:
# /usr/lib/plexmediaserver/Plex\ Media\ Scanner --list

# Movies
/usr/lib/plexmediaserver/Plex\ Media\ Scanner -srp -c 3

# TV Shows
/usr/lib/plexmediaserver/Plex\ Media\ Scanner -srp -c 4

