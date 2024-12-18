# Automatic detection of thermal panels

The project aims to perform automatic detection of thermal panels on georeferenced raster images of Switzerland with a deep learning approach. Detailed documentation of the project and results can be found on the [STDL technical website](https://tech.stdl.ch/PROJ-TPNL/). <br>

**Table of content**

- [Requirements](#requirements)
    - [Hardware](#hardware)
    - [Software](#software)
    - [Installation](#installation)
- [Getting started](#getting-started)
    - [Files structure](#files-structure)
    - [Data](#data)
    - [Scripts](#scripts)
    - [Workflow instructions](#workflow-instructions)
- [Contributors](#contributors)
- [Disclaimer](#disclaimer)

## Requirements

### Hardware

The project has been run on a 32 GiB RAM machine with a 16 GiB GPU (NVIDIA Tesla T4) compatible with [CUDA](https://detectron2.readthedocs.io/en/latest/tutorials/install.html). 

### Software

- Ubuntu 20.04
- Python version 3.8 
- PyTorch version 1.10
- CUDA version 11.3
- GDAL version 3.0.4
- object-detector version [2.3.2](https://github.com/swiss-territorial-data-lab/object-detector/releases/tag/v2.3.2)

### Installation

Install GDAL:

```
$ sudo apt-get install -y python3-gdal gdal-bin libgdal-dev gcc g++ python3.8-dev
```

Python dependencies can be installed with `pip` or `conda` using the `requirements.txt` file (compiled from `requirements.in`) provided. We advise using a [Python virtual environment](https://docs.python.org/3/library/venv.html).

- Create a Python virtual environment
```
$ python3.8 -m venv <dir_path>/<name of the virtual environment>
$ source <dir_path>/<name of the virtual environment>/bin/activate
```

- Install dependencies
```
$ pip install -r requirements.txt
```

- `requirements.txt` has been obtained by compiling `requirements.in`. Recompiling the file might lead to libraries version changes:
```
$ pip-compile requirements.in
```

## Getting started

### Files structure

The folders/files of the project `proj-tpnl` (in combination with the `object-detector`) are organised as follows. Path names and values can be customised by the user:

<pre>.
├── config                                          # configurations files folder
│   ├── config_det.yaml                             # detection workflow
│   ├── config_trne.yaml                            # training and evaluation workflow
│   └── detectron2_config_dqry.yaml                 # detectron 2
├── data                                            # folder containing the input data
│   ├── AoI                                         # available on request
│   ├── ground_truth                                                             
│   ├── layers                                      # available on request 
│   └── categories_ids.json                         # class dictionnary     
├── functions
│   ├── constants.py                              
│   └── misc.py                                
├── images                                          
├── models                                          # trained models
├── output                                          # outputs folders
│   ├── det                            
│   └── trne
├── sandbox                                         # folder containing scripts in developments. Their execution is not guarentee. README are present in each sub-folders
│   ├── post-processing  
│   │   ├── extract-prediction 
│   │   ├── filter-prediction 
│   │   └── prediction-thresholding                      
│   ├── pre-processing       
│   │   ├── tile-generator  
│   │   └── wmts-geoquery                                      
│   └── prepare_data_customed_tiles.py  
dataset 
├── scripts
│   ├── filter_detections.py                        # script detections filtering 
│   ├── merge_detections.py                         # script merging adjacent detections and attributing class
│   └── prepare_data.py                             # script preparing data to be processed by the object-detector scripts
├── .gitignore                                      
├── LICENSE
├── README.md                                      
├── requirements.in                                 # list of python libraries required for the project
└── requirements.txt                                # python dependencies compiled from requirements.in file
</pre>


## Data

Below, the description of input data used for this project. 

- images: [_SWISSIMAGE Journey_](https://map.geo.admin.ch/#/map?lang=fr&center=2660000,1190000&z=1&bgLayer=ch.swisstopo.pixelkarte-farbe&topic=ech&layers=ch.swisstopo.swissimage-product@year=2024;ch.swisstopo.swissimage-product.metadata@year=2024) is an annual dataset of aerial images of Switzerland from 1946 to today. The images are downloaded from the [geo.admin.ch](https://www.geo.admin.ch/fr) server using [XYZ](https://api3.geo.admin.ch/services/sdiservices.html#xyz) connector. 
- ground truth: labels vectorized by domain experts. We have at our disposal ground truth from the Argau canton (FHNW), Neucĥatel canton and Geneva canton vectorized for the year 2020.


## Scripts

The `proj-tpnl` repository contains scripts to prepare and post-process the data and results. Hereafter a short description of each script and a workflow graph:

<p align="center">
<img src="./images/tpnl_det_workflow.png?raw=true" width="100%">
<br />
</p>

1. `prepare_data.py`: format labels and produce tiles to be processed for the object detection.
2. `merge_detections.py`: merge adjacent detections cut by tiles into a single detection and attribute the class (the class of the maximum area).
3. `filter_detections.py`: filter detections by overlap with building footprints and other values such as score and polygon area.

Object detection is performed with tools present in the [`object-detector`](https://github.com/swiss-territorial-data-lab/object-detector) git repository. 


## Workflow instructions

The workflow can be executed by running the following list of actions and commands. Adjust the paths and input values of the configuration files accordingly. The contents of the configuration files in angle brackets must be assigned.

**Training and evaluation**: 

```
$ python scripts/prepare_data.py config/config_trne.yaml
$ stdl-objdet generate_tilesets config/config_trne.yaml
$ stdl-objdet train_model config/config_trne.yaml
$ tensorboard --logdir output/output_trne/logs
```

Open the following link with a web browser: `http://localhost:6006` and identify the iteration minimising the validation loss and select the model accordingly (`model_*.pth`) in `config_trne`.

```
$ stdl-objdet make_detections config/config_trne.yaml
$ stdl-objdet assess_detections config/config_trne.yaml
$ python scripts/merge_detections config/config_trne.yaml
```

**Inference**: 

```
$ python scripts/prepare_data.py config/config_det.yaml
$ stdl-objdet generate_tilesets config/config_det.yaml
$ stdl-objdet make_detections config/config_det.yaml
$ python scripts/merge_detections.py config/config_trne.yaml
$ python scripts/filter_detections.py config/config_trne.yaml
```

Don't forget to assign the desired year to the url in `config_det.yaml` when you download tiles from the server with `generate_tilesets.py`.


Optional:
```
$ python scripts/result_review.py config/config_det.yaml
```

## Contributors

`proj-tpnl` was made possible with the help of several contributors (alphabetical):

Alessandro Cerioni, Nils Hamel, Clémence Herny, Adrian Meyer, Huriel Reichel

## Disclaimer

Depending on the end purpose, we strongly recommend users not take for granted the detections obtained through this code. Indeed, results can exhibit false positives and false negatives, as is the case in all approaches based on deep learning.