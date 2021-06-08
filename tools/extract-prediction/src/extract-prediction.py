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
import pandas as pd
import geopandas as gpd
import networkx


def pairs(lst):
    """
    # cf. https://stackoverflow.com/a/9354040
    """
    i = iter(lst)
    first = prev = item = next(i)
    for item in i:
        yield prev, item
        prev = item
    yield item, first


if __name__ == "__main__":

    # Argument and parameter specification
    parser = argparse.ArgumentParser(description="Prediction extractor tool (STDL)")
    parser.add_argument('--prediction', type=str  , help='Prediction geographic file')
    parser.add_argument('--score'     , type=float, help='Score threshold')
    parser.add_argument('--output'    , type=str  , help='Output geographical file')
    args = parser.parse_args()

    # Import predictions
    geo_predict = gpd.read_file( args.prediction )

    # Extract predictions with score higher or equal to the specified threshold
    geo_extract = geo_predict[ geo_predict.score >= args.score ].copy()

    # Display information
    print( f'File {os.path.basename(args.prediction)} was read with {len(geo_predict)} prediction(s), of which {len(geo_extract)} are above the chosen threshold value (= {args.score}).' )

    del geo_predict

    # Detect overlapping predictions
    print("Detecting overlapping predictions...")
    overlapping_predictions_dict = {}

    # We first sjoin the concerned gdf with itself...
    _tmp_gdf = gpd.sjoin(geo_extract, geo_extract, how='inner', op='intersects')
    # ...then we filter out rows including twins
    _tmp_gdf = _tmp_gdf[_tmp_gdf.index != _tmp_gdf.index_right].copy()
    # ...finally we collect results
    for idx, row in _tmp_gdf.iterrows():

        if idx not in overlapping_predictions_dict.keys():
            overlapping_predictions_dict[idx] = []

        overlapping_predictions_dict[idx].append(row.index_right)
    del _tmp_gdf
    print("...done.")

    # Identify groups/clusters of overlapping predictions
    overlapping_predictions_list = []
    for k, v in overlapping_predictions_dict.items():
        _tmp_list = [k] + list(v)
        overlapping_predictions_list.append(sorted(_tmp_list))

    del overlapping_predictions_dict
    del _tmp_list

    # cf. https://stackoverflow.com/a/9354040
    g = networkx.Graph()
    for sub_list in overlapping_predictions_list:
        for edge in pairs(sub_list):
            g.add_edge(*edge)

    groups = list(networkx.connected_components(g))
    del overlapping_predictions_list
    del g
    
    # Replace overlapping predictions by merged ones

    # Display information
    print( f'{len(groups)} clusters were found: merging predictions belonging to the same cluster...' )

    out_geo_extract = geo_extract.copy()

    for group in groups:

        index = list(group)
        
        _tmp_gdf = gpd.GeoDataFrame(geo_extract.loc[index], crs=geo_extract.crs)
        
        new_geometry = _tmp_gdf.geometry.unary_union
        new_dataset = ",".join(_tmp_gdf.dataset.unique())
        
        # compute a new score as the mean of the input scores, weighted by the area
        # TODO: improve the algorithm in order to prevent intersecting areas from being "counted twice"
        _projected_tmp_gdf = _tmp_gdf.to_crs(epsg=2056)  
        _projected_tmp_gdf['area_weighted_score'] = _projected_tmp_gdf.apply(lambda row: row.score*row.geometry.area, axis=1)
        new_score = _projected_tmp_gdf.area_weighted_score.sum() / _projected_tmp_gdf.geometry.area.sum()
        
        df = pd.DataFrame.from_records([{'score': new_score, 'dataset': new_dataset}])
        new_feature = gpd.GeoDataFrame(df, geometry=[new_geometry])

        out_geo_extract.drop(index=index, inplace=True)
        out_geo_extract = pd.concat([
            out_geo_extract,
            new_feature
        ])

    print("...done.")

    out_geo_extract.to_crs(epsg=4326).to_file( args.output , driver='GeoJSON' )

    # Display information
    print( f'File {os.path.basename(args.output)} was written, with {len(out_geo_extract)} feature(s).' )
