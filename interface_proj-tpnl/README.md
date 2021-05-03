## Overview

This set of scripts and configuration files are related to the _thermal panel_ detection case. The detector is initially trained on data of the _Aargau Kanton_ using _swissimage_ from _swisstopo_ and labels of the _SolAI_ project of the _FHNW_.

## Usage

This script uses the standard _yaml_ configuration file of the object detector by reading its dedicated section.

The script is used in the following way :

    $ python3 prepare_data.py --config [yaml_config] [--logger [logging_config]]

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
      label:
        shapefile: [LABEL_SHAPEFILE]
        redfact: 0.9
      output_folder: ../output

for tiles defined through a shapefile. The lables section can be missing, indicating that tiles are prepared for inference only.

The _redfact_ key allows to specify the reduction factor of the label that is performed before removing empty tiles (tiles with empty intersection with all labels). Reducing the labels before removing empty tiles allows to force tiles with small overlap with labels to be removed. This allows not to consider tiles with a small portion of label at its edges.

In both case, the _srs_ key provides the working geographical frame in order for all the input data to work together.

### CSV Specified Tiles

The _CSV_ file has to give the bounding box of each tile to consider. Each _CSV_ are expected to contain at least the following values :

    x_min, y_min, x_max, y_max

giving the tile bounding box coordinates. The _CSV_ file is specified using the _csv_ key in the _tiling_ section.

The _split_ key in the tiling section allows the script to divide the tiles into sub-tiles.

### Shapefile Specified Tiles

In case a _shapefile_ is used for tiles definition, it has to contain the tiles as simple _polygons_ providing the shape of each tile.

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
    $ python [detector_path]/scripts/train_model.py config_NE.yaml
    $ python [detector_path]/scripts/make_prediction.py config_NE.yaml
    $ python [detector_path]/scripts/assess_predictions.py config_NE.yaml
