#!/bin/python
# -*- coding: utf-8 -*-

#  Detector interface
#
#      Nils Hamel - nils.hamel@alumni.epfl.ch
#      Huriel Reichel - huriel.ruan@gmail.com
#      Alessandro Cerioni
#      Copyright (c) 2020-2022 Republic and Canton of Geneva
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
import geopandas as gpd
import rasterio
import pandas as pd
import argparse
import sys

pm_argparse = argparse.ArgumentParser()

pm_argparse.add_argument( '-i', '--input', type=str  ,     help='input geojson path' )
pm_argparse.add_argument( '-d', '--dem',   type=str  ,     help='input DEM path' )
pm_argparse.add_argument( '-o', '--output',type=str  ,     help='output geojson path' )
pm_argparse.add_argument( '-a', '--area' , type=float  ,     default = 1728.,  help='area threshold. Default to 1728' )
pm_argparse.add_argument( '-s', '--score', type=float,     default = 0.9  , help='score threshold. Default to 0.9' )
pm_argparse.add_argument( '-e', '--elevation', type=float, default = 1155 , help='elevation threshold. Default to 1155' )
pm_argparse.add_argument( '--distance', type=float, default = 8, help="distance for union. Default to 8")

pm_args = pm_argparse.parse_args()

input = gpd.read_file(pm_args.input)
input = input.to_crs(2056)

total = len(input)
input["area"] = input['geometry'].area/ 10**6

input = input[input.area > pm_args.area]
ta = len(input)
ar = total - ta
print(str(ar) + " predictions were removed by area threshold")

input = input[input['score'] > pm_args.score]
ts = len(input)
sr = ta - ts
print(str(sr) + " predictions were removed by score threshold")

input['x'] = input.centroid.x
input['y'] = input.centroid.y

r = rasterio.open(pm_args.dem)

row, col = r.index(input.x,input.y)
values = r.read(1)[row,col]

input['elev'] = values

input = input[input['elev'] < pm_args.elevation]
te = len(input)
se = ts - te
print(str(se) + " predictions were removed by elevation threshold")
print(str(te) + " predictions left")

# Create empty data frame
geo_merge = gpd.GeoDataFrame()

# Merge close labels using buffer and unions
geo_merge = input.buffer( +pm_args.distance, resolution = 2 )
geo_merge = geo_merge.geometry.unary_union
geo_merge = gpd.GeoDataFrame(geometry=[geo_merge], crs = input.crs )
geo_merge = geo_merge.explode().reset_index(drop=True)
geo_merge = geo_merge.buffer( -pm_args.distance, resolution = 2 )

td = len(geo_merge)
print(str(td) + " predictions left after joining resulting polygons")

geo_merge.to_file(pm_args.output, driver='GeoJSON')

