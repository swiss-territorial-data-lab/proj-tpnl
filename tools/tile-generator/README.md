## Overview

This script allows to create a user-specified tiles that covers the polygons specified through a _shapefile_.

## Usage

The script is used based on a _shapefile_ containing one or more polygons :

    $ python3 grid-generator.py --labels [polygon_shapefile] 
                                --size [tile_size]
                                --output [output_directory]
                                [--x-shift/--y-shift [grid origin shift]]


The _size_ allows to specify the width (and height) of the tile to produce. This value is interpreted into perspective of the geographical coordinates of the labels _shapefile_.

The output directory is used to dump the _shapefile_ containing the computed tiles. The name of each file is generated according to the provided parameters.

The _shift_ value allows to translate the origin of the grid on which tiles are attached. The default value is zero. The shifts are specified in proportion of the specified tile _size_.

The following illustrations give examples of computed tiles of _50m_ size with two value of shifts using buildings as labels :

<p align="center">
<img src="doc/tile-example-1?raw=true" width="35%">
&nbsp;
<img src="doc/tile-example-2?raw=true" width="35%">
<br />
<i>Obtained tiles of 50m using building as labels</i>
</p>


