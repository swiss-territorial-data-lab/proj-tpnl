## Overview

This set of scripts and configuration files are related to the _quarry/exploitation sites_ detection case. The detector is initially trained on _swissimage_ from _swisstopo_ using the _TLM_ data of _swisstopo_ for the labels.

## Usage

For this case, the _thermal panel (TPNL)_ case script is used. See its documentation on the [following page](../interface_proj-tpnl)

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
