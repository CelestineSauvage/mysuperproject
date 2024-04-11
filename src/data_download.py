import sys
import logging
import argparse
from apiDataCollection.APIConstants import DataCollectorConstants
from apiDataCollection import DataCollector
from helpers.Chronometer import Chronometer

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
    
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(format=log_format, level=logging.INFO)

    args = parse_args()

    #FTDataCollector = DataCollector.FTDataCollector()
    #FTDataCollector.collect(args)

    apecDataCollector = DataCollector.ApecDataCollector()
    apecDataCollector.collect(args)


if __name__ == "__main__":
    sys.exit(main())
