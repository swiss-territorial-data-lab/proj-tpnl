## Overview

This script allows to extract the prediction out of the detector _GeoJSON_ based on a provided threshold value.

The strategy consists in filtering the prediction through a provided threshold and to then merge overlapping predictions that passed the threshold filter.

## Usage

The script expects then a prediction _GeoJSON_ file all geometry containing a _score_ value normalised in _[0,1]_ and the filtering threshold :

    $ python3 extract-prediction.py --prediction [prediction GeoJSON]
                                    --score [threshold value]
                                    --output [Output GeoJSON]

The results of the filtering/merging are dumped in the provided output _GeoJSON_ (destination is replaced in case it exists).

The following images give an illustration of the extraction process showing the original and filtered predictions :

<p align="center">
<img src="doc/prediction.webp?raw=true" width="35%">
&nbsp;
<img src="doc/filter-result.webp?raw=true" width="35%">
<br />
<i>Left : Detector predictions - Right : Threshold filtering results</i>
</p>

The value of the filtering threshold is usually obtained by training analysis.
