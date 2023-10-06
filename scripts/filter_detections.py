#!/bin/python
# -*- coding: utf-8 -*-

# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import os
import sys
import time
import argparse
import yaml

import geopandas as gpd
import pandas as pd
import rasterio
from sklearn.cluster import KMeans

sys.path.insert(0, '.')
from functions import misc
from functions.constants import DONE_MSG

from loguru import logger
logger = misc.format_logger(logger)


if __name__ == "__main__":

    # Chronometer
    tic = time.time()
    logger.info('Starting...')

    # Argument and parameter specification
    parser = argparse.ArgumentParser(description="The script filters the detection of potential Mineral Extraction Sites obtained with the object-detector scripts")
    parser.add_argument('config_file', type=str, help='input geojson path')
    args = parser.parse_args()

    logger.info(f"Using {args.config_file} as config file.")

    with open(args.config_file) as fp:
        cfg = yaml.load(fp, Loader=yaml.FullLoader)[os.path.basename(__file__)]

    # Load input parameters
    YEAR = cfg['year']
    DETECTIONS = cfg['detections']
    SCORE = cfg['score']
    AREA = cfg['area']
    DISTANCE = cfg['distance']
    OUTPUT = cfg['output']

    written_files = [] 

    # Read detections file
    detections = gpd.read_file(DETECTIONS)
    detections = detections.to_crs(2056)
    total = len(detections)
    logger.info(f"{total} input shapes")

    # Merge close features
    detections_merge = gpd.GeoDataFrame()
    detections_merge = detections.buffer(0.2, resolution=2).geometry.unary_union
    detections_merge = gpd.GeoDataFrame(geometry=[detections_merge], crs=detections.crs)  
    detections_merge = detections_merge.explode(index_parts=True).reset_index(drop=True)   
    detections_merge.geometry = detections_merge.geometry.buffer(-0.2, resolution=2)  
    detections_merge['index_merge'] = detections_merge.index
    detections_join = gpd.sjoin(detections_merge, detections, how='inner', predicate='intersects')
    detections_merge = detections_join.dissolve(by='index_merge', aggfunc='max')

    td = len(detections_merge)
    logger.info(f"{td} clustered detections remains after shape union (distance threshold = {DISTANCE} m)")

    # Filter dataframe by score value
    detections_score = detections_merge[detections_merge.score > SCORE]
    sc = len(detections_score)
    logger.info(f"{td - sc} detections were removed by score filtering (score threshold = {SCORE})")

    # Discard polygons with area under the threshold 
    detections_area = detections_score[detections_score.area > AREA]
    ta = len(detections_area)
    logger.info(f"{sc - ta} detections were removed by area filtering (area threshold = {AREA} m2)")

    # Final gdf
    detection_filtered = detections_area.drop(['index_right', 'crs', 'dataset'], axis=1)
    logger.info(f"{len(detection_filtered)} detections remaining after filtering")

    # Formatting the output name of the filtered detection  
    feature_path = OUTPUT.replace('{score}', str(SCORE)).replace('0.', '0dot') \
        .replace('{year}', str(int(YEAR))) \
        .replace('{area}', str(int(AREA))) \
        .replace('{distance}', str(DISTANCE)).replace('0.', '0dot')
    detection_filtered.to_file(feature_path)

    written_files.append(feature_path)
    logger.success(f"{DONE_MSG} A file was written: {feature_path}")  

    logger.info("The following files were written. Let's check them out!")
    for written_file in written_files:
        logger.info(written_file)

    # Stop chronometer  
    toc = time.time()
    logger.info(f"Nothing left to be done: exiting. Elapsed time: {(toc-tic):.2f} seconds")

    sys.stderr.flush()