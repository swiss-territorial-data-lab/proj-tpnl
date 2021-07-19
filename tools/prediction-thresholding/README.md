## Overview

This script allows to extract the prediction out of the detector _GeoJSON_ based on a series of provided threshold values.

The prediction are first filtered based on their polygons' ares value, then through score value. Following, with the input of a Digital Elevation Model an elevation thresholding is processed. Finally the predicition polygons are joined (spatial join) with a distance criteria. 

## Usage

The script expects then a prediction _GeoJSON_ file with all geometries containing a _score_ value normalised in _[0,1]_ and the filtering threshold :

    $ python prediction-thresholding.py --input [prediction GeoJSON]
    				         --dem [digital elevation model GeoTiff]
                                    --score [threshold value]
                                    --area [threshold value]
                                    --distance [threshold value]
                                    --output [Output GeoJSON]

The results of the filtering/merging are dumped in the provided output _GeoJSON_ (destination is replaced in case it exists).

The following images give an illustration of the extraction process showing the original and filtered predictions :

<p align="center">
<img src="doc/before.png?raw=true" width="35%">
&nbsp;
<img src="doc/after.png?raw=true" width="35%">
<br />
<i>Left : Detector predictions - Right : Threshold filtering results</i>
</p>

The value of the filtering threshold is usually obtained by the training validation set analysis or other more advanced methods.
