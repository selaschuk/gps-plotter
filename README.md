# gps-plotter
Simple Script for Collecting and Plotting NEMA GPS sentences

Assumes your NEMA Sentences are prefixed with a device ID like the following:
```
Dev-0032,$GPGGA,145635.0,5104.015927,N,11319.810693,W,1,11,0.8,977.0,M,-17.0,M,,*62
Dev-0054,$GPVTG,269.4,T,269.4,M,38.7,N,71.6,K,A*2F
```

Edit http://gps.server.com:8889/gps.json in gps.html to point to wherever gps.py is running

Requires [pynmea2](https://github.com/Knio/pynmea2)

HTML from this fantastic stackoverflow response: http://stackoverflow.com/questions/14771422/google-map-v3-auto-refresh-markers-only
