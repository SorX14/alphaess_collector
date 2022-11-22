#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import configparser
import logging
import traceback
import asyncio
import sys
from datetime import datetime
import time
from alphaess_modbus import Reader
from mysql.connector import connect, Error
import os

def configure_logger():
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s [%(filename)s.%(funcName)s:%(lineno)d] %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

async def main(config):
    logger.debug("Starting connector...")

    reader: Reader = Reader(debug=False)

    while True:
        try:
            start_time = time.time()
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            pv = await reader.get_value("inverter_power_total")
            grid = await reader.get_value("total_active_power_grid_meter")    
            load = grid + pv

            voltage = await reader.get_value("voltage_of_a_phase_grid")
            frequency = await reader.get_value("frequency_grid")

            try:
                with connect(
                    host=config['host'],
                    user=config['user'],
                    password=config['pass'],
                    database=config['database'],
                    port=config['port']
                ) as connection:
                    logger.info(f"{current_time}: PV: {pv}W Grid: {grid}W Load: {load}W {voltage}V @ {frequency}Hz")

                    qry = f"INSERT INTO {config['table']} (`time`, `pv`, `grid`, `load`, `voltage`, `frequency`) VALUES (%s, %s, %s, %s, %s, %s);"
                    data = (current_time, pv, grid, load, voltage, frequency)

                    with connection.cursor() as cursor:
                        cursor.execute(qry, data)
                        connection.commit()
            except Error as e:
                logger.error('MySQL error :(')
                logger.error(e)

            # Try to get a reading every 1 second
            await asyncio.sleep(1 - (time.time() - start_time)) 
        except IOError as e:
            # If something goes wrong, we'll give it a few seconds before retrying
            logger.error('IOError :(')
            logger.error(e)
            await asyncio.sleep(5) 

if __name__ == "__main__":
    try:
        path_current_directory = os.path.dirname(__file__)
        path_config_file = os.path.join(path_current_directory, "config.ini")
        
        logger = configure_logger()
        config = configparser.ConfigParser()
        config.read(path_config_file)

        loop = asyncio.run(main(config['mysql']))
    except (ValueError, Exception) as e:
        logger.debug(str(e))
        logger.debug(traceback.format_exc())
    except KeyboardInterrupt:
        pass

