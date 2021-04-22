## Overview

This repository gives access to the script required between the data used with the object detector and the object detector itself.

The proposed script are related to specific cases, and then specific data and formats, and are used to transform and prepare the data to be used in the object detector.

## detector-interface

The following links gives access to the specialised documentation of each interface, grouped by cases :

* [Thermal Panels (TPNL)](interface_proj-tpnl)
* [Quarry (DQRY)](interface_proj-dqry)

## Auxiliary Tools

This repository comes with a few tools that can be useful to prepare the datasets :

* [Tiles generator](tools/tile-generator)

## Copyright and License

**detector-interface** - Nils Hamel, Adrian Meyer, Huriel Reichel, Alessandro Cerioni <br >
Copyright (c) 2020-2021 Republic and Canton of Geneva

This program is licensed under the terms of the GNU GPLv3. Documentation and illustrations are licensed under the terms of the CC BY 4.0.

## Dependencies

The _detector-interface_ comes with the following dependencies :

* Python 3.6 or superior

Packages can be installed either by pip or conda (*conda forge*):

* geopandas 0.8.0
* Shapely 1.7.1
