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
│   └── detectron2_config.yaml                      # detectron 2
├── data                                            # folder containing the input data
│   ├── AoI                                         # available on request
│   ├── ground_truth                                # available on request                             
│   ├── layers                                      # available on request 
│   └── categories_ids.json                         # class dictionnary     
├── functions
│   ├── constants.py    
│   ├── metrics.py                             
│   └── misc.py                                
├── images                                          
├── models                                          # trained models
├── output                                          # outputs folders
│   ├── det                            
│   └── trne
├── sandbox                                         # folder containing scripts in developments.
│   ├── post-processing  
│   │   ├── extract-prediction 
│   │   ├── filter-prediction 
│   │   └── prediction-thresholding                      
│   ├── pre-processing       
│   │   ├── tile-generator  
│   │   └── wmts-geoquery                                      
│   └── prepare_data_customed_tiles.py  
├── scripts
│   ├── mask_buildings.py                           # script applying a building footprint mask to an image 
│   ├── merge_detections.py                         # script merging adjacent detections and attributing class
│   ├── prepare_data.py                             # script preparing data to be processed by the object-detector scripts
│   └── review_detections.py                        # script matching GT with detections
├── .gitignore                                      
├── LICENSE
├── README.md                                      
├── requirements.in                                 # list of python libraries required for the project
└── requirements.txt                                # python dependencies compiled from requirements.in file
</pre>


## Data

Below, the description of input data used for this project. 

- images: [_SWISSIMAGE Journey_](https://map.geo.admin.ch/#/map?lang=fr&center=2660000,1190000&z=1&bgLayer=ch.swisstopo.pixelkarte-farbe&topic=ech&layers=ch.swisstopo.swissimage-product@year=2024;ch.swisstopo.swissimage-product.metadata@year=2024) is an annual dataset of aerial images of Switzerland from 1946 to today. The images are downloaded from the [geo.admin.ch](https://www.geo.admin.ch/fr) server using [XYZ](https://api3.geo.admin.ch/services/sdiservices.html#xyz) connector. 
- ground truth: labels vectorized by experts in the field. We have the ground truth for the Canton of Argau (FHNW), the Canton of Neucĥatel and the Canton of Geneva vectorized for the year 2020 and for the Canton of Vaud vectorized for the year 2023.
- building footprints: provided by the [swissTLM3D](https://www.swisstopo.admin.ch/fr/modele-du-territoire-swisstlm3d).
- category_ids.json: categories attributed to the detections.
- models: the trained models used to produce the results presented in the documentation are available on request.

## Scripts

The `proj-tpnl` repository contains scripts to prepare and post-process the data and results. Hereafter a short description of each script and a workflow graph:

<p align="center">
<img src="./images/tpnl_det_workflow.png?raw=true" width="100%">
<br />
</p>

1. `prepare_data.py`: format labels and produce tiles to be processed for the object detection.
2. `mask_buildings.py`: apply a mask to keep only buildings pixel in an image.
3. `merge_detections.py`: merge adjacent detections cut by tiles into a single detection and attribute the class (the class of the maximum area). It also offers the possbility to filter detections by confidence score and building footprints.
4. `review_detections.py`: match a shapefile indicating the presence of an energy installation on a building with the detections obtained with the model.

Object detection is performed with tools present in the [`object-detector`](https://github.com/swiss-territorial-data-lab/object-detector) git repository. 


## Workflow instructions

The workflow can be executed by running the following list of actions and commands. Adjust the paths and input values of the configuration files accordingly. The contents of the configuration files in square brackets must be assigned. 

**Training and evaluation**: 

Prepare the data:
```
$ python scripts/prepare_data.py config/config_trne.yaml
$ stdl-objdet generate_tilesets config/config_trne.yaml
```

A mask can be applied on the images to keep only building pixels (optional):
```
$ python scripts/result_analysis.py config/config_trne.yaml
```

Train the model:
```
$ stdl-objdet train_model config/config_trne.yaml
$ tensorboard --logdir output/trne/logs
```

Open the following link with a web browser: `http://localhost:6006` and identify the iteration minimising the validation loss and select the model accordingly (`model_*.pth`) in `config_trne`. For the provided parameters, `model_0009999.pth` is the default one.

Perform and assess detections:
```
$ stdl-objdet make_detections config/config_trne.yaml
$ stdl-objdet assess_detections config/config_trne.yaml
```

Finally, the detection obtained by tiles can be merged when adjacent and a new assessment is performed:
```
$ python scripts/merge_detections.py config/config_trne.yaml
```

**Inference**: 

Copy the selected trained model to the folder `models`:
```
$ mkdir models
$ cp output/trne/logs/<selected_model_pth> models
```

Process images:
```
$ python scripts/prepare_data.py config/config_det.yaml
$ stdl-objdet generate_tilesets config/config_det.yaml
$ stdl-objdet make_detections config/config_det.yaml
$ python scripts/merge_detections.py config/config_det.yaml
```

Review the results:
```
$ python scripts/review_detection.py config/config_det.yaml
```

## Sandbox

Additional scripts originated from previous version of the project are loacted in the sandbox folder. They permit to pre- and post-processed the data and detections. A README file is present in each sub-folders. Their execution is not guarentee. 


## Contributors

`proj-tpnl` was made possible with the help of several contributors (alphabetical):

Alessandro Cerioni, Nils Hamel, Clémence Herny, Adrian Meyer, Huriel Reichel

## Disclaimer

Depending on the end purpose, we strongly recommend users not take for granted the detections obtained through this code. Indeed, results can exhibit false positives and false negatives, as is the case in all approaches based on deep learning.