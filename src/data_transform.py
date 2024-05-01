import sys
import logging
import argparse
from helpers.Chronometer import Chronometer
from transform import JobsProcess
from transform.APIConstants import DataCollectorConstants
from pathlib import Path
import datetime

ARG_PATH = DataCollectorConstants.ARG_PATH.value


def parse_args():
    # TODO add subparser for each data source

    parser = argparse.ArgumentParser(
        description='Download jobs from France API in json files')
    parser.add_argument(f"{ARG_PATH}", type=str,
                        help='directory where json files will be store')
    parser.add_argument("source", help='source of data')

    args = parser.parse_args()
    args_dict = vars(args)
    return args_dict


def main():
    chrono = Chronometer()

    args = parse_args()

    now = datetime.datetime.now(datetime.UTC)
    dt_string = now.strftime("%Y_%m_%d_%H_%M_%S")

    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(filename=f"logs/log_transform_{args["source"]}_{dt_string}.log",
                        format=log_format, level=logging.INFO)

    logger = logging.getLogger(__name__)

    directory = Path(args[ARG_PATH])

    if args["source"] == "0":
        logger.info("Source : France Travail")
        transformation = JobsProcess.FTJobsProcess()

    elif args["source"] == "1":

        logger.info("Source : APEC")
        transformation = JobsProcess.ApecJobsProcess()

    else:
        raise ValueError("Source must be 0 or 1")

    transformation.process_directory(directory)


if __name__ == "__main__":
    sys.exit(main())
