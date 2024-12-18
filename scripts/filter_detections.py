import argparse
import os
import sys
import time
import yaml

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio

sys.path.insert(0, '.')
import functions.fct_misc as misc
from functions.constants import DONE_MSG

from loguru import logger
logger = misc.format_logger(logger)


def check_gdf_len(gdf):
    """Check if the GeoDataFrame is empty. If True, exit the script

    Args:
        gdf (GeoDataFrame): detection polygons
    """

    try:
        assert len(gdf) > 0
    except AssertionError:
        logger.error("No detections left in the dataframe. Exit script.")
        sys.exit(1)


def none_if_undefined(cfg, key):
    
    return cfg[key] if key in cfg.keys() else None


if __name__ == "__main__":

    # Chronometer
    tic = time.time()
    logger.info('Starting...')

    # Argument and parameter specification
    parser = argparse.ArgumentParser(description="The script post-process the detections obtained with the object-detector")
    parser.add_argument('config_file', type=str, help='input geojson path')
    args = parser.parse_args()

    logger.info(f"Using {args.config_file} as config file.")

    with open(args.config_file) as fp:
        cfg = yaml.load(fp, Loader=yaml.FullLoader)[os.path.basename(__file__)]

    # Load input parameters
    WORKING_DIR = cfg['working_dir']
    DETECTIONS = cfg['detections']
    BUILDINGS = cfg['buildings'] if 'buildings' in cfg.keys() else None
    SCORE_THD = cfg['score_threshold']
    AREA_THD = cfg['area_threshold']

    os.chdir(WORKING_DIR)
    logger.info(f'Working directory set to {WORKING_DIR}')

    logger.info(f'Canton: {CANTON}')

    written_files = [] 

    # Convert input detections to a geodataframe 
    detections_gdf = gpd.read_file(DETECTIONS)
    detections_gdf = detections_gdf.to_crs(2056)
    if 'tag' in detections_gdf.keys():
        detections_gdf = detections_gdf[detections_gdf['tag']!='FN']
    detections_gdf['area'] = detections_gdf.geometry.area 
    detections_gdf['det_id'] = detections_gdf.index
    total = len(detections_gdf)
    logger.info(f"{total} detections")

    detections_gdf = misc.check_validity(detections_gdf, correct=True)

    # Filter dataframe by with building intersection
    if BUILDINGS:
        buildings_gdf = gpd.read_file(BUILDINGS)
        buildings_gdf = tiles_gdf.to_crs(2056)        
        left_join = gpd.sjoin(detections_gdf, buildings_gdf, how='left', predicate='intersects', lsuffix='left', rsuffix='right')
        detections_gdf = left_join[left_join.label_id.notnull()].copy().drop_duplicates()
    building = len(detections_score_gdf)
    logger.info(f"{total - building} detections were removed by score filtering (score threshold = {SCORE_THD})")

    # Filter dataframe by score value
    check_gdf_len(detections_gdf)
    detections_score_gdf = detections_gdf[detections_gdf.score > SCORE_THD]
    sc = len(detections_score_gdf)
    logger.info(f"{building - sc} detections were removed by score filtering (score threshold = {SCORE_THD})")

    detections_infos_gdf = detections_score_gdf.copy()

    # Discard polygons with area under a given threshold 
    check_gdf_len(detections_infos_gdf)
    detections_infos_gdf = detections_infos_gdf.explode(ignore_index=True)
    detections_infos_gdf['area'] = detections_infos_gdf.area
    tsjoin = len(detections_infos_gdf)
    detections_infos_gdf = detections_infos_gdf[detections_infos_gdf.area > AREA_THD]
    ta = len(detections_infos_gdf)
    logger.info(f"{tsjoin - ta} detections were removed by area filtering (area threshold = {AREA_THD} m2)")

    check_gdf_len(detections_infos_gdf)

    # Final gdf
    logger.info(f"{len(detections_infos_gdf)} detections remaining after filtering")

    # Formatting the output name of the filtered detection  
    feature = f'{DETECTIONS[:-5]}_threshold_score-{SCORE_THD}_area-{int(AREA_THD)}_elevation-{int(ELEVATION_THD)}'.replace('0.', '0dot') + '.gpkg'
    detections_infos_gdf.to_file(feature)

    written_files.append(feature)
    logger.success(f"{DONE_MSG} A file was written: {feature}")  

    logger.info("The following files were written. Let's check them out!")
    for written_file in written_files:
        logger.info(written_file)

    # Stop chronometer  
    toc = time.time()
    logger.info(f"Nothing left to be done: exiting. Elapsed time: {(toc-tic):.2f} seconds")

    sys.stderr.flush()