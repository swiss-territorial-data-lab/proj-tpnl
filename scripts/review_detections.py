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
    FILE = cfg['file']
    OUTPUT = cfg['output']

    written_files = [] 

    # Read detections file
    data = gpd.read_file(FILE)

    data_gt = data[data['TP_2020'] == 'yes'] 
    data_det = data[data['detection'] == 'yes'] 

    logger.info(f"Number of GT = {len(data_gt)}")
    logger.info(f"Number of detection = {len(data_det)}")
    logger.info("Sucess of detection = " + "{:.0%}".format(len(data_det) / len(data_gt)))

    logger.info("The following files were written. Let's check them out!")
    for written_file in written_files:
        logger.info(written_file)

    # Stop chronometer  
    toc = time.time()
    logger.info(f"Nothing left to be done: exiting. Elapsed time: {(toc-tic):.2f} seconds")

    sys.stderr.flush()