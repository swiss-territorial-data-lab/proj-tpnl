#!/bin/python
# -*- coding: utf-8 -*-

#  Detector interface
#
#      Nils Hamel - nils.hamel@alumni.epfl.ch
#      Huriel Reichel
#      Copyright (c) 2020 Republic and Canton of Geneva
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import os, sys
import math
import geopandas as gpd
from shapely.geometry import Polygon, LineString, Point

if __name__ == "__main__":

    # Argument and parameter specification
    parser = argparse.ArgumentParser(description="Prediction extractor tool (STDL)")
    parser.add_argument('--prediction', type=str  , help='Prediction geographic file')
    parser.add_argument('--score'     , type=float, help='Score threshold')
    parser.add_argument('--output'    , type=str  , help='Output geographical file')
    args = parser.parse_args()

    # Import predictions
    geo_predict = gpd.read_file( args.prediction )

    # Display information
    print( f'File {os.path.basename(args.prediction)} readed with {len(geo_predict)} prediction(s)' )

    # Extract predictions with score higher or equal to the specified threshold
    geo_extract = geo_predict[ geo_predict.score >= args.score ]

    # Merge overlapping predictions
    geo_extract = geo_extract.geometry.unary_union
    geo_extract = gpd.GeoDataFrame( geometry=[geo_extract], crs = 'EPSG:4326' )
    geo_extract = geo_extract.explode().reset_index( drop=True )

    # Display information
    print( f'File {os.path.basename(args.prediction)} filtered with {len(geo_extract)} prediction(s)' )

    # Export filtering prediction
    geo_extract.to_crs( epsg='4326' ).to_file( args.output, driver='GeoJSON' )
