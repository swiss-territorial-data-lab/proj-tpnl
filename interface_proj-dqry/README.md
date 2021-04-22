## Overview


## Usage

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
