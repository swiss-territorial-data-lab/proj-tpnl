#!/bin/python
# -*- coding: utf-8 -*-

#  Detector interface
#
#      Nils Hamel - nils.hamel@alumni.epfl.ch
#      Huriel Reichel
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
import yaml
import json
import os, sys
import glob
import geopandas as gpd
import numpy

from osgeo import gdal, osr
from shapely.geometry import Polygon

# Add local library path for the import above this line
sys.path.append( os.path.normpath( os.path.dirname( os.path.realpath(__file__) ) + '/../lib' ) )

import COCO



def prepare_split( length, split_seed, split_proportion ):

    # Assign seed to RNG
    numpy.random.seed( split_seed )

    # Compute random permutation
    permute = numpy.random.permutation( length )

    # Compute ranges size
    trn_set = int( length * split_proportion[0] )
    tst_set = int( length * split_proportion[1] )

    # Make sure to keep all elements
    val_set = length - trn_set - tst_set

    # Return index array
    return permute[0:trn_set], permute[trn_set:trn_set+tst_set], permute[trn_set+tst_set:trn_set+tst_set+val_set]
    


def prepare_tile( tile_path, epsg ):

    # Prepare tile geoset
    geo_tile = gpd.GeoDataFrame( columns=[ 'geometry', 'file', 'xsize', 'ysize', 'xmin', 'ymin', 'xmax', 'ymax' ], geometry='geometry' )

    # Initialise index
    index = 0

    # Parsing tile image files
    for geotiff in glob.glob( tile_path + '/*.tif' ):

        # Display progress
        print( "Pushing :", os.path.basename( geotiff ) )

        # Create GDAL object
        geodata = gdal.Open( geotiff )

        # Extract geographical information
        w = geodata.RasterXSize
        h = geodata.RasterYSize
        t = geodata.GetGeoTransform()

        # Extract boundaries
        x_min = t[0]
        y_min = t[3] + w * t[4] + h * t[5]
        x_max = t[0] + w * t[1] + h * t[2]
        y_max = t[3]

        # Check EPSG of tile       
        if int( osr.SpatialReference( wkt = geodata.GetProjection() ).GetAttrValue( 'AUTHORITY',1 ) ) != int( epsg ):
            raise ValueError( "Tile image is not in expected coordinate frame" )

        # Compose and push tile polygon
        geo_tile.loc[ index, "geometry" ] = Polygon( [

            ( x_min, y_min ),
            ( x_max, y_min ),
            ( x_max, y_max ),
            ( x_min, y_max )

        ] )

        # Push tile uid
        geo_tile.loc[ index, "file" ] = os.path.basename( geotiff )

        # Push tile pixel size
        geo_tile.loc[ index, "xsize" ] = w
        geo_tile.loc[ index, "ysize" ] = h

        # Push tile geographical information
        geo_tile.loc[ index, "xmin" ] = x_min
        geo_tile.loc[ index, "ymin" ] = y_min
        geo_tile.loc[ index, "xmax" ] = x_max
        geo_tile.loc[ index, "ymax" ] = y_max

        # Update index
        index = index + 1

        # Developmend clamp (to make test on small amount of tile. Be sure
        # you disable the error raise on empty tile if you use this.
        if index > 50:
            break

    # Return tile layer
    return geo_tile.set_crs( epsg = epsg )


def tile_coco( geo_tile, geo_link, geo_index, coco_geotiff_path, coco_year, coco_class, coco_category, coco_output ):

    # Create COCO object : see ../lib/COCO.py
    coco = COCO.COCO()

    # Set COCO file basic information
    coco.set_info(
        the_year=f"{coco_year}", 
        the_version="1.0", 
        the_description="STDL dataset", 
        the_contributor="STDL", 
        the_url="N/A"
    )

    # Insert COCO license
    coco_license = coco.license(
        the_name="On Demand (STDL)", 
        the_url="N/A"
    )
    coco_license_id = coco.insert_license( coco_license )

    # Insert COCO root class and category
    coco_category = coco.category(
        the_supercategory=coco_class,
        the_name=coco_category
    )
    coco_category_id = coco.insert_category(coco_category)

    # Parsing the tiles that are part of the provided split. These tiles are
    # all the result of image listing in the data conformation directory.
    for index in geo_index:

        # Display progress
        print( "COCO annotation : ", geo_tile.loc[index,"file"] )

        # Prepare COCO annotation for this tile
        coco_image = coco.image( coco_geotiff_path, geo_tile.loc[index,"file"], coco_license_id )

        # Insert image in COCO file
        coco_image_id = coco.insert_image( coco_image )

        # Create list of all label parts that belongs to the current
        # tile. This list is based on identifying the tile name appearing
        # in each label entries of the link layer.
        tile_labels = geo_link[ geo_link["file_right"] == geo_tile.loc[index,"file"] ]

        # If the list of label that belongs to the current tile is empty,
        # then something is wrong : no tile should be empty of any label
        # or label part
        if len( tile_labels ) == 0:
            raise ValueError( f'The tile {geo_tile.loc[index,"file"]} has no label or label part' )

        # Extract tile pixel size
        tile_x = float( geo_tile.loc[index,"xsize"] )
        tile_y = float( geo_tile.loc[index,"ysize"] )

        # Extract tile geographical information
        x_min = float( geo_tile.loc[index,"xmin"] )
        y_min = float( geo_tile.loc[index,"ymin"] )
        x_max = float( geo_tile.loc[index,"xmax"] )
        y_max = float( geo_tile.loc[index,"ymax"] )

        # Compute geographical span with pixel factor
        x_span = tile_x / ( x_max - x_min )
        y_span = tile_y / ( y_max - y_min )

        #print( x_min, y_min, x_max, y_max, tile_x, tile_y, x_span, y_span )

        # Parsing each labels that are associated to the current tile
        for _, tile_label in tile_labels.iterrows():

            # Extract label entity
            label_entity = geo_label.loc[ tile_label["index_right"], "geometry" ]

            # Assess label type
            if type( label_entity ) != Polygon:
                raise ValueError( f'Expects polygon for label, not {type( label_entity )}' )

            # Extract coordinates of polygon
            label_x, label_y = label_entity.exterior.coords.xy

            # Python things ...
            label_x = label_x.tolist()
            label_y = label_y.tolist()

            # Prepare compacted / xy-mixed coordinate list
            compacted_coords = []

            # Parsing coordinates
            for i in range( len( label_x ) ):

                # Convert coordinates from geographic to pixel and append to xy-mixed list
                compacted_coords.append( + ( label_x[i] - x_min ) * x_span )
                compacted_coords.append( - ( label_y[i] - y_min ) * y_span + tile_y )

                # Assess coordinates
                if compacted_coords[-2] < 0. or compacted_coords[-2] > tile_x:
                    raise ValueError( 'Label x-coordinates are outside of tile span' )
                if compacted_coords[-1] < 0. or compacted_coords[-1] > tile_y:
                    raise ValueError( 'Label y-coordinates are outside of tile span' )

            # Create COCO annotation
            print( 'Create COCO annotation' )
            coco_annotation = coco.annotation(
                coco_image_id,
                coco_category_id,
                [compacted_coords],
                the_iscrowd=0
            )

            # Insert COCO annotation
            print( 'Insert COCO annotation' )
            coco.insert_annotation( coco_annotation )

    # Write composed COCO file by dumping COCO JSON content
    with open( coco_output, 'w' ) as coco_stream:
        json.dump( coco.to_json(), coco_stream )



if __name__ == "__main__":

    # Arguments and parameters header
    parser = argparse.ArgumentParser(description="Object detector framework : Local dataset prepare process")

    # Push expected arguments and parameters
    parser.add_argument('--config', type=str, help='Framework process configuration YAML')

    # Process command line
    args = parser.parse_args()

    # Check configuration file
    try:

        # Read common section
        with open(args.config) as fp:
            common = yaml.load( fp, Loader=yaml.FullLoader )[ "common" ]

        # Read script-specific section
        with open(args.config) as fp:
            config = yaml.load( fp, Loader=yaml.FullLoader )[ os.path.basename(__file__) ]

    except Exception as error:
        if hasattr( error, 'message' ):
            print( error.message )
        else:
            print( error )
        sys.exit(1)

    # Check configuration content
    try:

        # Dataset root directory
        if not os.path.isdir( config["dataset"] ):
            raise ValueError( "Dataset root directory not found" )

        # Dataset conformation file
        if not os.path.isfile( os.path.join( config["dataset"], config["conformation"] ) ):
            raise ValueError( "Conformation file missing" )

    except Exception as error:
        if hasattr( error, 'message' ):
            print( error.message )
        else:
            print( error )
        sys.exit(1)

    # Try importing conformation content
    try:

        # Import conformation lines
        with open( os.path.join( config["dataset"], config["conformation"] ) ) as cfrfile:
            conformation = cfrfile.readlines()

    except Exception as error:
        if hasattr( error, 'message' ):
            print( error.message )
        else:
            print( error )
        sys.exit(1)

    # Debug
    if common["debug"]:
        print( conformation )

    # Check exportation path
    try:

        # Check if directory needs to be created
        if not os.path.isdir( common["working"] ):
            os.mkdir( common["working"] )

    except Exception as error:
        if hasattr( error, 'message' ):
            print( error.message )
        else:
            print( error )
        sys.exit(1)

    # Prepare data from dataset
    try:

        # Parsing conformation file lines
        for line in conformation:

            # Conformation line formatting
            current = line.rstrip('\n').strip()

            # Avoid comments
            if current[0] == '#' or current[0] == '%':
                continue

            # Decompose line
            decomp = current.split( ' ' )

            # Check line format consistency
            if len( decomp ) != 6:
                raise ValueError( "Conformation line format incorrect" )

            # Debug
            if common["debug"]:
                print( "Conformation line :", current )

            # Compose label path
            label_path = f'{config["dataset"]}/{decomp[0]}/{decomp[1]}/{decomp[2]}/{decomp[3]}/label/label.shp'

            # Check existence of label file
            if not os.path.isfile( label_path ):
                raise ValueError( "Label geographical file not found" )

            # Import label shapefile
            geo_label = gpd.read_file( label_path ).to_crs( epsg = decomp[3] )

            # Compose tile images path
            tile_path = f'{config["dataset"]}/{decomp[0]}/{decomp[1]}/{decomp[2]}/{decomp[3]}/tile/{decomp[4]}/geotiff/{decomp[5]}'

            # Check existence of tile directory
            if not os.path.isdir( tile_path ):
                raise ValueError( "Tile images directory not found" )

            # Check tile images and create tile layer
            geo_tile = prepare_tile( tile_path, decomp[3] )

            # Debug
            if common["debug"]:
                geo_tile.to_file( os.path.join( common["working"], 'tile.shp' ) )

            # Split label based on the tile bounding box -> Distribution of label parts on tiles
            geo_label = gpd.overlay( geo_label, geo_tile, how="intersection" )

            # Debug
            if common["debug"]:
                geo_label.to_file( os.path.join( common["working"], 'label-on-tile.shp' ) )

            # Compose split index array
            trn_index, tst_index, val_index = prepare_split( len( geo_tile ), config["split_seed"], config["split_prop"] )

            # Create link database between tile and label parts
            #
            # For each label, its tile is determined in order, for each tile to
            # have the list of all label part associated to it.
            geo_link = gpd.sjoin( geo_tile, geo_label, how = 'left' )

            # Debug
            if common["debug"]:
                geo_link.to_file( os.path.join( common["working"], 'tile-label-link.shp' ) )

            # Create COCO annotation of the different sets. The differents sets
            # are defined through the split procedure and the :
            #
            #   trn_index, tst_index, val_index
            #
            # arrays of index. Each array contains the tile index, according to
            # the built :
            #
            #   geo_tile
            #
            # geographical layer, of each specific set : training, validation
            # and testing. It follows that these array should not have any index
            # in common.

            # Create COCO annotation for the training set
            tile_coco( 
                geo_tile, 
                geo_link, 
                trn_index,
                tile_path,
                decomp[2], 
                common["class"],
                common["category"],
                os.path.join( common["working"], 'COCO_trn.json' )
            )

            # Create COCO annotation for the testing set
            tile_coco( 
                geo_tile, 
                geo_link, 
                tst_index,
                tile_path,
                decomp[2], 
                common["class"],
                common["category"],
                os.path.join( common["working"], 'COCO_tst.json' )
            )

            # Create COCO annotation for the validation set
            tile_coco( 
                geo_tile, 
                geo_link, 
                val_index,
                tile_path,
                decomp[2], 
                common["class"],
                common["category"],
                os.path.join( common["working"], 'COCO_val.json' )
            )

            # Parsing each tile based on listed geotiff in dataset
            #for index, single_tile in geo_tile.iterrows():

                # Create list of all label parts that belongs to the current
                # tile. This list is based on identifying the tile name appearing
                # in each label entries of the link layer.
            #    selection = geo_link[ geo_link["file_right"] == single_tile["file"] ]

                # If the list of label that belongs to the current tile is empty,
                # then something is wrong : no tile should be empty of any label
                # or label part
           #     if len( selection ) == 0:
           #         raise ValueError( f'The tile {single_tile["file"]} has no label or label part' )

                # Need to be done :
                #
                # For each tile -> create the COCO annotation based on the label
                # list (selection). The geographic transfromation need to be
                # applied to convert label geographical coordinates to image
                # pixel coordinates

                # Need to be done :
                #
                # Make sure the image are copied on the working directory for   
                # them to be available for the training of the detector. In
                # addition, COCO annotation must contain the path of the tile
                # image file.

                # Development assessment segment : confirm that all label for each tile are considered
                #geo_test = gpd.GeoDataFrame( columns=[ 'geometry' ], geometry='geometry' )
                #if len( selection ) > 0:
                #    for test_index, test_tile in selection.iterrows():
                #        print( "\t", test_index, test_tile["FID"] )
                #        geo_test.loc[ test_index, "geometry" ] = geo_label.loc[ test_tile["index_right"], "geometry" ]
                #    geo_test.loc[ len(geo_test), "geometry" ] = single_tile["geometry"]
                #    geo_test.set_crs( epsg = decomp[3] ).to_file( os.path.join( common["working"], f'{index}-tile.shp' ) )

            # Development : temporary confirmation prints
            #print( len( geo_tile ) )
            #print( len( trn_index ), trn_index )
            #print( len( tst_index ), tst_index )
            #print( len( val_index ), val_index )

    except Exception as error:
        if hasattr( error, 'message' ):
            print( error.message )
        else:
            print( error )
        sys.exit(1)

