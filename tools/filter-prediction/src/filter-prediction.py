#!/bin/python
# -*- coding: utf-8 -*-

#  Detector interface
#
#      Nils Hamel - nils.hamel@alumni.epfl.ch
#      Huriel Reichel
#      Alessandro Cerioni
#      Copyright (c) 2020-2021 Republic and Canton of Geneva
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
import pandas as pd
import geopandas as gpd

if __name__ == "__main__":

    # Argument and parameter specification
    parser = argparse.ArgumentParser(description="Prediction extractor tool (STDL)")
    parser.add_argument('--prediction', type=str  , help='Prediction geographic file')
    parser.add_argument('--filter'    , type=str  , help='Filter area geographic file')
    parser.add_argument('--mode'      , type=str  , help='Filtering mode (inside/outside)', default='inside')
    parser.add_argument('--export'    , type=str  , help='Exportation mode (polygon/point)', default='polygon')
    parser.add_argument('--output'    , type=str  , help='Output geographical file')
    args = parser.parse_args()

    # Import predictions
    geo_predict = gpd.read_file( args.prediction )

    # Display information
    print( f'Loaded predictions with {len(geo_predict)} entity(ies)' )

    # Import filtering layer
    geo_filter = gpd.read_file( args.filter )

    # Display information
    print( f'Loaded filtering layer with {len(geo_filter)} entity(ies)' )

    # Check filter mode
    if args.mode == 'outside':

        # Create list of prediction intersecting the filter layer
        geo_keep = gpd.sjoin( geo_predict, geo_filter, how="inner", op='intersects' )

        # Remove duplicated geometries
        geo_keep.drop_duplicates(subset=['geometry'],inplace=True)

        # Invert result of spatial join to collect outside predictions
        geo_keep = gpd.overlay( geo_predict, geo_keep, how='difference')

    elif args.mode == 'inside':

        # Create list of prediction intersecting the filter layer
        geo_keep = gpd.sjoin( geo_predict, geo_filter, how="inner", op='intersects' )

        # Remove duplicated geometries
        geo_keep.drop_duplicates(subset=['geometry'],inplace=True)

    else:

        # Display error
        print( 'Error : Filtering mode' )

        # Abort script
        sys.exit(1)

    # Display information
    print( f'Prediction(s) remaining after filtering : {len(geo_keep)}' )
    
    # Check filter mode
    if args.export == 'polygon':

        # Simple copy
        geo_export = geo_keep

    elif args.export == 'point':

        # Convert to point through centroid
        #
        # Warning : This procedure will only be suitable for specific type of
        # polygon for which the centroid is within the polygon. This is the case    
        # for convex polygon and part of the concave ones.
        geo_export = geo_keep['geometry'].centroid

    else:

        # Display error
        print( 'Error : Exportation mode' )

        # Abort script
        sys.exit(1)

    # Export filtering prediction
    geo_export.to_file( args.output )

    # Exit script with normal code
    sys.exit(0)
    
