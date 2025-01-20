import argparse
import os
import sys
import time
import yaml

import geopandas as gpd

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
    parser = argparse.ArgumentParser(description="The script compare the detection with the GT")
    parser.add_argument('config_file', type=str, help='input geojson path')
    args = parser.parse_args()

    logger.info(f"Using {args.config_file} as config file.")

    with open(args.config_file) as fp:
        cfg = yaml.load(fp, Loader=yaml.FullLoader)[os.path.basename(__file__)]

    # Load input parameters
    WORKING_DIR = cfg['working_dir']
    SUBVENTIONS_SHP = cfg['subventions_shp']
    BUILDINGS_SHP = cfg['buildings_shp']
    DETECTIONS_SHP = cfg['detections_shp']

    os.chdir(WORKING_DIR)
    logger.info(f'Working directory set to {WORKING_DIR}')

    # Read shapefiles
    subventions_gdf = gpd.read_file(SUBVENTIONS_SHP)
    buildings_gdf = gpd.read_file(BUILDINGS_SHP)
    detections_gdf = gpd.read_file(DETECTIONS_SHP)
    detections_gdf = detections_gdf[detections_gdf['det_category']=='thermal panel']
    detections_gdf['det_id'] = detections_gdf.index 

    buildings_wt_subventions_gdf = gpd.sjoin(buildings_gdf, subventions_gdf, how='left', predicate='intersects', lsuffix='left', rsuffix='right')
    buildings_wt_subventions_gdf = buildings_wt_subventions_gdf[buildings_wt_subventions_gdf.egid.notnull()].copy()
    buildings_wt_subventions_gdf = buildings_wt_subventions_gdf.drop_duplicates(subset='id')
    buildings_wt_detections_gdf = gpd.sjoin(buildings_gdf, detections_gdf, how='inner', predicate='intersects', lsuffix='left', rsuffix='right')
    buildings_wt_detections_gdf = buildings_wt_detections_gdf[buildings_wt_detections_gdf.det_id.notnull()].copy() 
    buildings_wt_detections_gdf = buildings_wt_detections_gdf.drop_duplicates(subset='id')

    buildings_ids = buildings_wt_subventions_gdf.id.unique().tolist()
    match_buildings_gdf = buildings_wt_detections_gdf[buildings_wt_detections_gdf.id.isin(buildings_ids)]

    logger.info(f"Number of buildings with a thermal panel subvention = {len(buildings_wt_subventions_gdf)}")
    logger.info(f"Number of buildings with a thermal panel detection = {len(buildings_wt_detections_gdf)}")
    logger.info(f"Number of buildings with both subvention and detection = {len(match_buildings_gdf)}")
    logger.info(f"Subvention detection accuracy = {(len(match_buildings_gdf)/len(buildings_wt_subventions_gdf)*100):.2f}%")

    # Stop chronometer  
    toc = time.time()
    logger.info(f"Nothing left to be done: exiting. Elapsed time: {(toc-tic):.2f} seconds")

    sys.stderr.flush()