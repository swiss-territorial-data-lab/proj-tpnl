## Overview

The section of the _yaml_ configuration file is expected as follows :

    prepare_data.py:
      srs: "EPSG:2056"
      tiling:
        csv: [TILE_CSV_FILE]
        split: 1
      label:
        shapefile: [LABEL_SHAPEFILE]
        redfact: 0.9
      output_folder: ../output

for tiles defined through _CSV_ file and :

    prepare_data.py:
      srs: "EPSG:2056"
      tiling:
        shapefile: [TILE_SHAPEFILE]
        split: 1
      label:
        shapefile: [LABEL_SHAPEFILE]
        redfact: 0.9
      output_folder: ../output

for tiles defined through a shapefile. The lables section can be missing, indicating that tiles are prepared for inference only.

The _redfact_ key allows to specify the reduction factor of the label that is performed before removing empty tiles (tiles with empty intersection with all labels). Reducing the labels before removing empty tiles allows to force tiles with small overlap with labels to be removed. This allows not to consider tiles with a small portion of label at its edges.

In both case, the _srs_ key provides the working geographical frame in order for all the input data to work together.

## CSV Specified Tiles

The _CSV_ file has to give the bounding box of each tile to consider. Each _CSV_ are expected to contain at least the following values :

    x_min, y_min, x_max, y_max

giving the tile bounding box coordinates. The _CSV_ file is specified using the _csv_ key in the _tiling_ section.

The _split_ key in the tiling section allows the script to divide the tiles into sub-tiles.

## Shapefile Specified Tiles

In case a _shapefile_ is used for tiles definition, it has to contain the tiles as simple _polygons_ providing the shape of each tile.

The _split_ key in the tiling section allows the script to divide the tiles into sub-tiles.
