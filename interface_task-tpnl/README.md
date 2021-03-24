## Overview

This set of scripts and data are related to the _thermal panel_ detection case. The detector is trained on data of the _Aargau Kanton_ using _swissimage_ from _swisstopo_ and labels of the _solai_ project of the _FHNW_.

## Usage

This script uses the standard _yaml_ configuration file of the object detector by adding its own section name after the script itself.

The script is used in the following way :

    $ python3 prepare_data.py --config [yaml_config] [--logger [logging_config]]

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

Currently, the label are provided through a simple _shapefile_ containing the polygon of the labels.

## Ressources

Two files are provided along the prepare script :

* config.yaml example
* logging.conf example

The logging format file can be used as provided. The configuration _YAML_ has to be adapted in terms of input and output location and files.

## Training and Validation

As the data are prepared using the proposed script, the following procedure can be followed in the appropriate environment :

    $ cd [process_directory]
    $ python [detector_path]/scripts/generate_training_sets.py [yaml_config]
    $ cd [output_directory]
    $ tar -cvf images-256.tar COCO_{trn,val,tst}.json && \
      tar -rvf images-256.tar {trn,val,tst}-images-256 && \
      gzip < images-256.tar > images-256.tar.gz && \
      rm images-256.tar
    $ cd -
    $ python [detector_path]/scripts/make_predictions.py config_NE.yaml
    $ python [detector_path]/scripts/assess_predictions.py config_NE.yaml
