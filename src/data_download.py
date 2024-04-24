import sys
import logging
import argparse
from helpers.APIConstants import DataCollectorConstants
from extract import DataCollector
from helpers.Chronometer import Chronometer
import datetime
from pathlib import Path

ARG_DATE_MIN = DataCollectorConstants.ARG_DATE_MIN.value
ARG_DATE_MAX = DataCollectorConstants.ARG_DATE_MAX.value
ARG_PUBLISHED_SINCE = DataCollectorConstants.ARG_PUBLISHED_SINCE.value
ARG_DEPARTMENTS = DataCollectorConstants.ARG_DEPARTMENTS.value
ARG_PATH = DataCollectorConstants.ARG_PATH.value


def parse_args():
    # TODO add subparser for each data source

    parser = argparse.ArgumentParser(
        description='Download jobs from France API in json files')
    parser.add_argument(f"{ARG_PATH}", type=str,
                        help='directory where json files will be store')
    parser.add_argument("source", help='source of data')
    parser.add_argument(f"--{ARG_DEPARTMENTS}",
                        help='specified department, if not, all departments are dl')
    parser.add_argument(f"--{ARG_PUBLISHED_SINCE}",
                        help="1, 3, 7, 14 or 31 last day(s)")
    # TODO FRANCE TRAVAIL API RETURN CODE 400
    parser.add_argument(f"--{ARG_DATE_MIN}",
                        help="format YYYY-MM-DD")
    parser.add_argument(f"--{ARG_DATE_MAX}",
                        help="format YYYY-MM-DD")

    args = parser.parse_args()
    args_dict = vars(args)
    return args_dict


def main():
    chrono = Chronometer()

    args = parse_args()

    now = datetime.datetime.now(datetime.UTC)
    dt_string = now.strftime("%Y_%m_%d_%H_%M_%S")

    log_file_name = f"logs/log_extract_{args["source"]}_{dt_string}.log"
    log_file_path = Path(log_file_name)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(filename=log_file_path,
                        format=log_format, level=logging.INFO)

    logger = logging.getLogger(__name__)

    if args["source"] == "0":
        logger.info("Source : France Travail")
        FTDataCollector = DataCollector.FTDataCollector()
        FTDataCollector.collect(args)

    elif args["source"] == "1":

        logger.info("Source : APEC")
        apecDataCollector = DataCollector.ApecDataCollector()
        apecDataCollector.collect(args)

    else:
        raise ValueError("Source must be 0 or 1")


if __name__ == "__main__":
    sys.exit(main())
