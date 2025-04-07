#!/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import time
import argparse
import yaml
from glob import glob
from tqdm import tqdm

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.mask import mask
from rasterio.features import rasterize
from shapely.geometry import Polygon, mapping

sys.path.insert(0, '.')
import functions.misc as misc

from loguru import logger
logger = misc.format_logger(logger)

# Define functions ------------------------------

def poly_from_utm(polygon, transform):
    poly_pts = []
    
    for i in np.array(polygon.exterior.coords):
        
        # Convert polygons to the image CRS
        poly_pts.append(~transform * tuple(i))
        
    # Generate a polygon object
    new_poly = Polygon(poly_pts)
    return new_poly


if __name__ == "__main__":

    # Start chronometer
    tic = time.time()
    logger.info('Starting...')

    # Argument and parameter specification
    parser = argparse.ArgumentParser(description="The script prepares the ground truth dataset to be processed by the object-detector scripts")
    parser.add_argument('config_file', type=str, help='Framework configuration file')
    args = parser.parse_args()

    logger.info(f"Using {args.config_file} as config file.")
 
    with open(args.config_file) as fp:
        cfg = yaml.load(fp, Loader=yaml.FullLoader)[os.path.basename(__file__)]

    WORKING_DIR = cfg['working_dir']
    BUILDINGS_SHP = cfg['buildings_shp']
    IMAGE_FOLDER = cfg['image_dir']
    TRANSPARENCY = cfg['transparency']

    os.chdir(WORKING_DIR)

    logger.info('Import data...')
    buildings_gdf = gpd.read_file(BUILDINGS_SHP)
    tiles = glob(os.path.join(IMAGE_FOLDER, '*.tif'))

    if buildings_gdf.crs != 'epsg:3857':
        buildings_gdf = buildings_gdf.to_crs(epsg=3857)

    logger.info('Process vector data...')
    buildings_gdf = buildings_gdf.buffer(0)
    merged_buildings_geoms = buildings_gdf.unary_union

    for tile in tqdm(tiles, desc='Produce masks', total=len(tiles)):

        if TRANSPARENCY:
            geoms_list = [mapping(merged_buildings_geoms)]

            with rasterio.open(tile) as src:
                mask_image, mask_transform = mask(src, geoms_list)
                mask_meta = src.meta
                
            mask_meta.update({'transform': mask_transform})
            filepath = os.path.join(os.makedirs((os.path.join(IMAGE_FOLDER, 'masked_images')),
                                os.path.splitext(os.path.basename(tile))[0] + '.tif'), exist_ok=True)
            
            with rasterio.open(filepath, 'w', **mask_meta) as dst:
                dst.write(mask_image)

        else:
            with rasterio.open(tile, "r") as src:
                tile_img = src.read()
                tile_meta = src.meta

            im_size = (tile_meta['height'], tile_meta['width'])

            polygons = [poly_from_utm(geom, src.meta['transform']) for geom in merged_buildings_geoms.geoms]
            mask_image = rasterize(shapes=polygons, out_shape=im_size)

            mask_meta = src.meta.copy()
            mask_meta.update({'count': 1, 'dtype': 'uint8', 'nodata': 99})
   
            filepath = os.path.join(os.makedirs((os.path.join(IMAGE_FOLDER, 'mask')),
                                os.path.splitext(os.path.basename(tile))[0] + '.tif'), exist_ok=True)
            
            with rasterio.open(filepath, 'w', **mask_meta) as dst:
                dst.write(mask_image, 1)

    logger.success(f'The masks were written in the folder {os.path.join(IMAGE_FOLDER, "mask")}.')