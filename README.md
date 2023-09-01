## Overview

This repository provides a suite of scripts and configuration files to perform automatic detections of thermal panels with Deep Learning methods on georeferenced raster images.<br>
The detector is initially trained on data of the _Aargau Kanton_ using _SWISSIMAGE_ (2020 mosaic) from _swisstopo_ and labels of the _SolAI_ project of the _FHNW_.<br>
The project `proj-tpnl` provides the preparation and post-processing scripts to be used along with the scripts in the repository `object-detector` developed by the STDL to perform object detection and segmentation.

**TOC**
- [Requirements](#requirements)
    - [Hardware](#hardware)
    - [Installation](#installation)
- [Files structure](#files-structure)
- [Workflow instructions](#workflow-instructions)
- [Copyright and License](#copyright-and-license)

## Requirements

### Hardware

The scripts have been run with Ubuntu 20.04 OS on a 32 GiB RAM machine with 16 GiB GPU (NVIDIA Tesla T4) compatible with [CUDA](https://detectron2.readthedocs.io/en/latest/tutorials/install.html) to use the library [detectron2](https://github.com/facebookresearch/detectron2), dedicated to object detection with Deep Learning algorithms. <br>

### Installation

The scripts have been developed with Python 3.8 using PyTorch version 1.10 and CUDA version 11.3. 
If not already done install GDAL:

    sudo apt-get install -y python3-gdal gdal-bin libgdal-dev gcc g++ python3.8-dev

All the dependencies required for the project are listed in `requirements.in` and `requirements.txt`. To install them:

- Create a Python virtual environment

        $ python3 -m venv <dir_path>/[name of the virtual environment]
        $ source <dir_path>/[name of the virtual environment]/bin/activate

- Install dependencies

        $ pip install -r requirements.txt

- _requirements.txt_ can be recompile from file _requirements.in_. Recompiling the file might lead to libraries version changes:

        $ pip-compile requirements.in

* pandas 1.5.3 is recommended to avoid dependencies depreciation.
* geopandas 0.8.0
* Shapely 1.7.1


## Files structure

The `proj-tpnl` repository (https://github.com/swiss-territorial-data-lab/proj-tpnl) contains scripts to prepare and post-process the datasets:

In addition, object detection is performed by tools developed in `object-detector` git repository. A description of the scripts used is presented [here](https://github.com/swiss-territorial-data-lab/object-detector)

The general folders/files structure of the project `proj-tpnl` is organized as follows. The path names can be customized by the end-user, and * indicates numbers that can vary:

<pre>.
├── config                                          # configurations files folder
│   ├── config.yaml                                 # project configuration file
│   ├── detectron2_config_tpnl.yaml                 # detectron 2 configuration file 
│   └── logging.conf                                # logging configuration
├── input                                           # inputs folders. Have to be created by the end-user 
│   ├── input-label.csv                             # label coordinates saved in .csv file
│   └── input-tiles.shp                             # tiles shapefile
├── output                                          # results folder
│   ├── all-images-[PIXEL SIZE]                     # images downloaded from wmts server (XYZ values)
│   │   ├── *.json
│   │   └── *.tif
│   ├── logs                                        # folder containing trained model 
│   │   ├── inference
│   │   │   ├── coco_instances_results.json
│   │   │   └── instances_predictions.pth
│   │   ├── events.out.tfevents.*.[MACHINE NAME].*.0
│   │   ├── last_checkpoint
│   │   ├── metrics.json                            # computed metrics for the given interval and bin size
│   │   ├── model_*.pth                             # saved trained model at a given iteration *
│   │   └── model_final.pth                         # last iteration saved model
│   ├── sample_tagged_images                        # examples of annoted prediction on images (XYZ values)
│   │   └── pred_*.png
│   │   └── tagged_*.png
│   │   └── trn_pred_*.png
│   │   └── tst_pred_*.png
│   │   └── val_pred_*.png
│   ├── trn-images-[PIXEL SIZE]                     # tagged images train DataSet  
│   │   └── *.tif
│   ├── tst-images-[PIXEL SIZE]                     # tagged images test DataSet
│   │   └── *.tif
│   ├── val-images-[PIXEL SIZE]                     # tagged images validation DataSet
│   │   └── *.tif
│   ├── clipped_labels.geojson                      # labels shape clipped to tiles shape 
│   ├── COCO_trn.json                               # COCO annotations on train DS
│   ├── COCO_tst.json                               # COCO annotations on test DS
│   ├── COCO_val.json                               # COCO annotations on validation DS
│   ├── img_metadata.json                           # images info
│   ├── labels.json                                 # labels geometries
│   ├── metrics_ite-*                               # metrics value at threshold value for the optimum model iteration * (saved manually after run assess_prediction.py)
│   ├── lr.svg                                      # learning rate plot (downloaded from tensorboard)
│   ├── precision_vs_recall.html                    # plot precision vs recall
│   ├── split_aoi_tiles.geojson                     # tagged DS tiles 
│   ├── tagged_predictions.gpkg                     # tagged predictions (TP, FP, FN) 
│   ├── tiles.json                                  # tiles geometries
│   ├── total_loss.svg                              # total loss plot (downloaded from tensorboard)
│   ├── trn_metrics_vs_threshold.html               # plot metrics of train DS (r, p, f1) vs threshold values
│   ├── trn_predictions_at_0dot*_threshold.gpkg     # prediction results for train DS at a given score threshold * in geopackage
│   ├── trn_TP-FN-FP_vs_threshold.html              # plot train DS TP-FN-FP vs threshold values
│   ├── tst_metrics_vs_threshold.html               # plot metrics of test DS (r, p, f1) vs threshold values
│   ├── tst_predictions_at_0dot*_threshold.gpkg     # prediction results for test DS at a given score threshold * in geopackage
│   ├── tst_TP-FN-FP_vs_threshold.html              # plot test DS TP-FN-FP vs threshold values
│   ├── val_metrics_vs_threshold.html               # plot metrics of validation DS (r, p, f1) vs threshold values
│   ├── val_predictions_at_0dot*_threshold.gpkg     # prediction results for validation DS at a given score threshold * in geopackage
│   ├── val_TP-FN-FP_vs_threshold.html              # plot validation DS TP-FN-FP vs threshold values
│   └── validation_loss.svg                         # validation loss curve (downloaded from tensorboard)
├── post-processing
│   ├── extract-prediction
│   │   ├── doc
│   │   │   ├── filter-result.webp
│   │   │   └── prediction.webp
│   │   ├── src
│   │   │   └── extract-prediction.py
│   │   └──README.md
│   ├── filter-prediction
│   │   ├── doc
│   │   │   ├── inside.webp
│   │   │   ├── inside-point.webp
│   │   │   ├── outside.webp
│   │   │   ├── outside-point.webp
│   │   │   └── prediction.webp
│   │   ├── src
│   │   │   └── filter-prediction.py
│   │   └── README.md
│   ├── prediction-thresholding
│   │   ├── doc
│   │   │   ├── after.png
│   │   │   └── before.png
│   │   ├── src
│   │   │   └── prediction-thresholding.py
│   │   └── README.md
├── pre-processing
│   ├── tile-generator
│   │   ├── doc
│   │   │   ├── tile-example-1.webp
│   │   │   ├── tile-example-2.webp
│   │   │   ├── tile-example-3.webp
│   │   │   └── tile-example-4.webp
│   │   ├── src
│   │   │   └── tile-generator.py
│   │   └──README.md
│   ├── wmts-geoquery
│   │   ├── dat
│   │   │   └── unitary-test-tiles-*.shp
│   │   ├── src
│   │   │   └── wmts-geoquery.py
│   │   └── README.md
├── scripts
│   └── prepare_data.py                             # script preparing files to run the object-detector scripts
├── .gitignore                                      # content added to this file is ignored by git 
├── LICENCE
├── README.md                                       # presentation of the project, requirements and execution of the project 
├── requirements.in                                 # python dependencies (modules and packages) required by the project
└── requirements.txt                                # compiled from requirements.in file. List of python dependencies for virtual environment creation
</pre>

## Workflow instructions

Following the end-to-end, the workflow can be run by issuing the following list of actions and commands:

Get `proj-tpnl` and `object-detector` repositories in the same folder.  

```bash
$ cd proj-tpnl/config
$ python3 -m venv <dir_path>/[name of the virtual environment]
$ source <dir_path>/[name of the virtual environment]/bin/activate
$ pip install -r requirements.txt
```

```bash
$ python3 ../scripts/prepare_data.py config.yaml
$ python3 ../../scripts/generate_tilesets.py config.yaml
$ python3 ../../scripts/train_model.py config.yaml
$ tensorboard --logdir ../output/output-trne/logs
```

Open the following link with a web browser: `http://localhost:6006` and identified the iteration minimizing the validation loss curve and the selected model name (**pth_file**) in `config` to run `make_predictions.py`. 

```bash
$ python3 ../../scripts/make_predictions.py config.yaml
$ python3 ../../scripts/assess_predictions.py config.yaml
```
Adapt the paths and input values of the configuration files accordingly.

## Disclaimer

Depending on the end purpose, we strongly recommend users not to take for granted the detections obtained through this code. Indeed, results can exhibit false positives and false negatives, as is the case in all Machine Learning-based approaches.

## Copyright and License

**proj-tpnl** - Nils Hamel, Adrian Meyer, Huriel Reichel, Alessandro Cerioni, Clémence Herny <br >
Copyright (c) 2020-2022 Republic and Canton of Geneva

This program is licensed under the terms of the GNU GPLv3. Documentation and illustrations are licensed under the terms of the CC BY 4.0.