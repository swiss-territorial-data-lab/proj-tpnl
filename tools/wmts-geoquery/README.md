# Overview

This script is made to allow query geographical tiles, defined by any bounding box, from a _WMTS_ services. Based on the bounding box and the service configuration, the scripts queries all the _WMTS_ tiles required to compose the desired geographical tile and produces georeferenced _GeoTIFF_ images as a result.

The tiles are defined through a geographical file, typically a _shapefile_, that is provided to the script as parameter.

# Usage

The script is used in the following way :

    $ python3 -Wignore wmts-geoquery.py --url [WMTS capabilities URL]
                                        --layer [WMTS layer identifier]
                                        --tiles [Tiles shapefile]
                                        --width [Width of tile, in pixels]
                                        --time  [Any valid year for the layer]

The _URL_ has to point to the _WMTS_ service capabilities _XML_ for the script to fetch the required information.

The layer name has to be the one specified in the _WMTS_ service capabilities.

In the _shapefile_, the tile are defined each by a rectangular (or square) polygon. The bounding box are extracted from the polygon to compose the _WMS_-like query before to translate it into _WMTS_ queries.

The width is provided in pixels according to the desired resolution. It is the responsibility of the user to ensure the bounding box and pixel width does not lead to overshoot the image ground sample distance.

It is then assumed that all the tiles defined in the provided _shapefile_ are of the same size, as receiving the same pixel width. The pixel height is deduced from the tile aspect ratio.

The time value is provided only in case the data is available as a _WMTS_ parameter.

# Development Notes

_GDAL linux_ binaries are used, through a system call, by the script to compose the tiles _GeoTIFF_ image. In the future, this features should be part of the script itself.

In addition, the script uses temporary files, that are stored by default on the _linux_ :

    /run/shm

_ramfs_. This location can be changed by using the --tmp parameter.
