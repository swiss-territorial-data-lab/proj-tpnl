# Automatic detection of thermal pannels

The project aims to perform automatic detection of thermal panels on georeferenced raster images of Switzerland with a deep learning approach. Detailed documentation of the project and results can be found on the [STDL technical website](https://tech.stdl.ch/PROJ-TPNL/). <br>

**TOC**
- [Requirements](#requirements)
    - [Hardware](#hardware)
    - [Software](#software)
    - [Installation](#installation)
- [Getting started](#getting-started)
    - [Files structure](#files-structure)
    - [Data](#data)
    - [Scripts](#scripts)
    - [Workflow instructions](#workflow-instructions)

## Requirements

### Hardware

The scripts have been run on a 32 GiB RAM machine with 16 GiB GPU (NVIDIA Tesla T4) compatible with [CUDA](https://detectron2.readthedocs.io/en/latest/tutorials/install.html). 

### Software

- Ubuntu 20.04
- Python version 3.8
- PyTorch version 1.10
- CUDA version 11.3
- GDAL version 3.0.4
- object-detector .
- pandas 1.5.3
- geopandas 0.8.0
- Shapely 1.7.1

### Installation

Install GDAL:

```
sudo apt-get install -y python3-gdal gdal-bin libgdal-dev gcc g++ python3.8-dev
```

Python dependencies can be installed with `pip` or `conda` using the `requirements.txt` file (compiled from `requirements.in`) provided. We advise using a [Python virtual environment](https://docs.python.org/3/library/venv.html).

- Create a Python virtual environment
```
$ python3 -m venv <dir_path>/<name of the virtual environment>
$ source <dir_path>/<name of the virtual environment>/bin/activate
```

- Install dependencies
```
$ pip install -r requirements.txt
```

- _requirements.txt_ has been obtained by compiling _requirements.in_. Recompiling the file might lead to libraries version changes:
```
$ pip-compile requirements.in
```


## Getting started

### Files structure

The `proj-tpnl` repository (https://github.com/swiss-territorial-data-lab/proj-tpnl) contains scripts to prepare and post-process the datasets and results:

In addition, object detection is performed by tools developed in `object-detector` git repository. A description of the scripts used is presented [here](https://github.com/swiss-territorial-data-lab/object-detector)

The general folders/files structure of the project `proj-tpnl` is organized as follows. 

<pre>.
├── config                                          # configurations files folder
│   ├── config_det.yaml                             # detection workflow
│   ├── config_trne.yaml                            # training and evaluation workflow
│   ├── detectron2_config_tpnl.yaml                 # detectron 2
│   └── logging.conf                                # logging configuration
├── functions                                    
│   ├── constant.py                
│   └── misc.py                               
├── input                                           # inputs folders
│   ├── input_det                                   # detection input data
│   └── input_trne                                  # training and evaluation input data
├── output                                          # output folders
│   ├── output_det                                  # output detections
│   └── output_trne                                 # training and evaluation outputs  
├── sandbox                                         # folder containing scripts in developments. Their execcution is not guarentee. README are present in each sub-folders
│   ├── post-processing  
│   │   ├── extract-prediction 
│   │   ├── filter-prediction 
│   │   └── prediction-thresholding                      
│   ├── pre-processing       
│   │   ├── tile-generator  
│   │   └── wmts-geoquery                                      
│   └── prepare_data_customed_tiles.py            
├── scripts
│   ├── post-processing.py                          # script post-processing the detections
│   ├── prepare_data.py                             # script preparing data to be processed by the object-detector scripts
│   └── results_review.py                           # script assessing the results 
├── .gitignore                                      
├── LICENSE
├── README.md                                      
├── requirements.in                                 # list of python libraries required for the project
└── requirements.txt                                # python dependencies compiled from requirements.in file
</pre>

## Data

Below, the description of input data used for this project. 

- images: [_SWISSIMAGE Journey_](https://www.swisstopo.admin.ch/en/maps-data-online/maps-geodata-online/journey-through-time-images.html) is an annual dataset of aerial images of Switzerland with pixel resolution from 10 cm to 50 cm. The images are downloaded from the [geo.admin.ch](https://www.geo.admin.ch/fr) server using [XYZ](https://developers.planet.com/docs/planetschool/xyz-tiles-and-slippy-maps/) connector. 
- ground truth: labels vectorized by domain experts. We have at our disposal ground truth from the Argau canton (FHNW), Neucĥatel canton and Geneva canton vectorized for the year 2020.


## Scripts

The `proj-tpnl` repository contains scripts to prepare and post-process the data and results:

1. `prepare_data.py`: format labels and produce tiles to be processed for the object detection.
2. `post_processing.py`: process the detection results to merge cut polygons by tiles, apply threshold score, remove detection not located on a roof.
3. `result_review.py`: compare post-process results with the ground truth.

Object detection is performed with tools present in the [`object-detector`](https://github.com/swiss-territorial-data-lab/object-detector) git repository. 


## Workflow instructions

The workflow can be executed by running the following list of actions and commands. Adjust the paths and input values of the configuration files accordingly. The contents of the configuration files in angle brackets must be assigned.

**Training and evaluation**: 

```bash
$ python scripts/prepare_data.py config/config_trne.yaml
$ stdl-objdet generate_tilesets config/config_trne.yaml
$ stdl-objdet train_model config/config_trne.yaml
$ tensorboard --logdir output/output_trne/logs
```

Open the following link with a web browser: `http://localhost:6006` and identify the iteration minimising the validation loss and select the model accordingly (`model_*.pth`) in `config_trne`.

```bash
$ stdl-objdet make_detections config/config_trne.yaml
$ stdl-objdet assess_detections config/config_trne.yaml
```

**Detection**: 

```bash
$ python scripts/prepare_data.py config/config_det.yaml
$ stdl-objdet generate_tilesets config/config_det.yaml
$ stdl-objdet make_detections config/config_det.yaml
$ python scripts/post_processing.py config/config_det.yaml
```

Don't forget to assign the desired year to the url in `config_det.yaml` when you download tiles from the server with `generate_tilesets.py`.

url: https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.swissimage-product/default/[YEAR]/3857/{z}/{x}/{y}.jpeg


Optional:
```bash
$ python scripts/result_review.py config/config_det.yaml
```

## Contributors

`proj-dqry` was made possible with the help of several contributors (alphabetical):

Alessandro Cerioni, Nils Hamel, Clémence Herny, Adrian Meyer, Huriel Reichel

## Disclaimer

Depending on the end purpose, we strongly recommend users not to take for granted the detections obtained through this code. Indeed, results can exhibit false positives and false negatives, as is the case in all Deep Learning-based approaches.