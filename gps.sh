#!/bin/bash
until python gps.py; do
    echo "Server 'gpsServer' crashed with exit code $?.  Respawning.." >&2
    sleep 1
done
