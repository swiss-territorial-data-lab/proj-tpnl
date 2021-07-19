## Overview

This script allows to filter prediction geometry based on the assumption that they can only be, or can only be outside, of specific areas.

In both cases, these areas needs to be provided to the script along with the predictions.

## Usage

Based on the prediction geometries and the definition of the areas, the script is used in the following way :

    $ python3 filter-prediction.py --prediction [Prediction geometries]
                                   --filter [Filtering areas geometries]
                                   --mode [Filtering mode]
                                   --export [Exportation mode]
                                   --output [Exportation file for filtered geometries]

The _mode_ parameter can be either _inside_ or _outside_. In the first case, only the geometries of the prediction that are within the area are kept. In the second case, only the prediction outside the area are kept.

The _export_ parameter can be either _polygon_ or _point_. In the first case, the kept prediction, after filtering, are exported as polygons.

In case _point_ is provided, the filtered predictions are transformed into points using their geometry centroid. The filtered prediction are then exported as point only, corresponding to their respective centroid.

As an example, the following predictions, in red, are filtered according to the building footprints, in black. As prediction should correspond to thermal panel, one assumes that prediction make sense only inside the geometry of the city buildings.

<p align="center">
<img src="doc/prediction.webp?raw=true" width="45%">
<br />
<i>Thermal panels prediction (red) and building footprints (black) - STDL/SITG</i>
</p>

If the _mode_ is set to _inside_, the following outcome are obtained when setting _export_ parameter to _polygon and to _point_ :

<p align="center">
<img src="doc/inside.webp?raw=true" width="45%">
&nbsp;
<img src="doc/inside-point.webp?raw=true" width="45%">
<br />
<i>Inside filtering exported as polygons (left) and points (right) </i>
</p>

The points are rendered with their corresponding geometry on the images, but the script only exports point when _export_ is set to _point_.

When the _mode_ is set to _outside_, the following outcomes are obtained :

<p align="center">
<img src="doc/outside.webp?raw=true" width="45%">
&nbsp;
<img src="doc/outside-point.webp?raw=true" width="45%">
<br />
<i>Inside filtering exported as polygons (left) and points (right) </i>
</p>

Again, the point are shown along with their corresponding geometries.
