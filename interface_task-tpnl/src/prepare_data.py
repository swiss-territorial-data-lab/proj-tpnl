#!/bin/python
# -*- coding: utf-8 -*-

import logging
import logging.config
import time
import argparse
import yaml
import os, sys, inspect
import requests
import geopandas as gpd
import pandas as pd
import json
import csv

from shapely.geometry import Polygon
from fiona.crs import from_epsg
from tqdm import tqdm

def compose_tiles( csv_row, tile_split ):

    """
    Overview :

    This function is responsible of transforming the provided bounding box,
    through the CSV row (dict), into rectangular tiles covering the bounding
    box.

    The amount of tile is deduced from the split value, which gives, when
    squared, the amount of computed tiles. The tiles are Polygon returned
    through a list.

    Parameter :

    csv_row : DictReader row

        CSV row giving the bounding box (x_min, y_min, x_max, y_max).

    tile_split : integer value

        Bounding box split value. Providing one produce one tile covering the
        bounding box. Providing two lead to four equal tiles covering the
        bounding box.

    Return :

    List : Shaply polygon list

        Return the tiles geometry through a list of polygons.
    """

    # Compose bounding box origin
    org_x = float( csv_row['x_min'] )
    org_y = float( csv_row['y_min'] )

    # Compute tiles edge
    egde_x = ( float( csv_row['x_max'] ) - float( csv_row['x_min'] ) ) / tile_split
    egde_y = ( float( csv_row['y_max'] ) - float( csv_row['y_min'] ) ) / tile_split

    # Initialise polygon list
    poly_list=[]

    # Parsing x-axis
    for x in range( tile_split ):

        # Parsing y-axis
        for y in range( tile_split ):

            # Compose and append polygon
            poly_list.append( Polygon( [

                ( org_x + egde_x * ( x     ), org_y + egde_y * ( y     ) ),
                ( org_x + egde_x * ( x + 1 ), org_y + egde_y * ( y     ) ),
                ( org_x + egde_x * ( x + 1 ), org_y + egde_y * ( y + 1 ) ),
                ( org_x + egde_x * ( x     ), org_y + egde_y * ( y + 1 ) ),
                ( org_x + egde_x * ( x     ), org_y + egde_y * ( y     ) )

            ] ) )

    # Return polygon list
    return poly_list

if __name__ == "__main__":

    # Argument and parameter specification
    parser = argparse.ArgumentParser(description="Front-end for data preparation in the context of thermal panels detection (STDL.TASK-TPNL)")
    parser.add_argument('--config', type=str, help='Framework configuration file')
    parser.add_argument('--logger', type=str, help='Log configuration file', default='logging.conf')
    args = parser.parse_args()

    try:

        # Logger configuration used to format script output
        logging.config.fileConfig('logging.conf')
        logger = logging.getLogger('root')

    except:

        # Display message & abort
        print('Unable to access logger configuration file')
        sys.stderr.flush()
        sys.exit(1)

    # Chronometer
    tic = time.time()

    try:

        # Import configuration file (YAML file)
        with open(args.config) as fp:
            cfg = yaml.load(fp, Loader=yaml.FullLoader)[os.path.basename(__file__)]

        # Logging info
        logger.info(f"Using {args.config} as config file.")

    except:
    
        # Logging info & abort
        logger.error(f"Unable to access {args.config} configuration file")
        sys.stderr.flush()
        sys.exit(1)

    # Check YAML key
    if 'output_folder' in cfg:

        # Create output directory if missing
        if not os.path.exists(cfg['output_folder']):
            os.makedirs(cfg['output_folder'])

    else:

        # Logging info & abort
        logger.error("Key <output_folder> missing")
        sys.stderr.flush()
        sys.exit(1)

    # Check YAML key
    if not 'label' in cfg:

        # Logging info & abort
        logger.error("Missing label key")
        sys.stderr.flush()
        sys.exit(1)

    # Check YAML key
    if 'shapefile' in cfg['label']:

        # Import label geometries from shapefile
        geo_label = gpd.read_file( cfg['label']['shapefile'] )

    else:

        # Logging info & abort
        logger.error("Missing source in label")
        sys.stderr.flush()
        sys.exit(1)

    # Check YAML key
    if not 'tiling' in cfg:

        # Logging info & abort
        logger.error("Missing tiling key")
        sys.stderr.flush()
        sys.exit(1)

    # Check YAML key
    if 'csv' in cfg['tiling']:

        # Check YAML key
        if not 'srs' in cfg['tiling']:

            # Logging info & abort
            logger.error("Missing srs key in tiling")
            sys.stderr.flush()
            sys.exit(1)

        # Check YAML key
        if not 'split' in cfg['tiling']:

            # Logging info & abort
            logger.error("Missing split key in tiling")
            sys.stderr.flush()
            sys.exit(1)

        # Match label and tiling coordinate frame
        geo_label = geo_label.to_crs( cfg['tiling']['srs'] )

        # Initialise tiling geometry
        geo_tiling = gpd.GeoDataFrame()

        # Import CSV data for tiling computation
        with open( cfg['tiling']['csv'], newline='') as csvfile:

            # Read CSV by dictionnary
            csvdata = csv.DictReader(csvfile, delimiter=',')

            # Initialise index
            index=0

            # Iterate over CSV rows
            for row in csvdata:

                # Compute polygon list
                poly_list = compose_tiles( row, cfg['tiling']['split'] )

                # Parsing polygon list
                for poly in poly_list:

                    # Retreive polygon bounding box
                    poly_bbox = poly.bounds

                    # Add tile geometry
                    geo_tiling.loc[index,'geometry'] = poly

                    # Add tile required columns
                    geo_tiling.loc[index,'id'   ] = f"({poly_bbox[0]}, {poly_bbox[1]}, 80)"
                    geo_tiling.loc[index,'title'] = f"XYZ tile ({poly_bbox[0]}, {poly_bbox[1]}, 80)"

                    # Update index
                    index = index + 1

        # set geographical frame of tiling geometry
        geo_tiling.set_crs( crs = cfg['tiling']['srs'], inplace = True )

    else:

        # Logging info & abort
        logger.error("Missing source in tiling")
        sys.stderr.flush()
        sys.exit(1)

    # Spatial join based on label to eliminate empty tiles (keeping only tiles with at least one label)
    geo_tiling = gpd.sjoin(geo_tiling, geo_label, how="inner")

    # Export labels into geojson, forcing epsg:4326 standard
    geo_label.to_crs(epsg='4326').to_file(os.path.join(cfg['output_folder'],'labels.geojson'),driver='GeoJSON')

    # Export tiles into geojson, forcing epsg:4326 standard
    geo_tiling.to_crs(epsg='4326').to_file(os.path.join(cfg['output_folder'],'tiles.geojson'),driver='GeoJSON')

    # Chronometer
    toc = time.time()

    # Display summary
    logger.info(f"Completed in {(toc-tic):.2f} seconds")

    # Flush error output
    sys.stderr.flush()

