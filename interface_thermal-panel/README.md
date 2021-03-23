## Overview

This set of scripts and data are related to the _thermal panel_ detection case. The detector is trained on data of the _Aargau Kanton_ using _swissimage_ from _swisstopo_ and labels of the _solai_ project of the _FHNW_.

## Usage

This script uses the standard _yaml_ configuration file of the object detector by adding its own section name after the script itself.

The script is used in the following way :

    $ python3 prepare_data.py --config [yaml\_config] [--logger [logging\_config]]

The section of the _yaml_ configuration file is expected as follows :

    prepare_data.py:
      tiling:
        csv: ./tiles
        srs: "EPSG:2056"
        split: 2
      label:
        shapefile: nw_thm_labels.shp
      output_folder: ../output

Currently, the input tiling definition is made through a simple _CSV_ file giving the bounding box of each tile to consider. Each _CSV_ are expected to contain at least the following values :

    x_min, y_min, x_max, y_max

giving the tile bounding box. The _CSV_ file is specified using the _csv_ key in the _tiling_ section. The _srs_ key has to provide the coordinate frame of the data in the _CSV_ file.

The _split_ key in the tiling section allows the script to divide the tiles into sub-tiles.

Currently, the label are provided through a simple _shapefile_ contiaing the polygon of the labels.
