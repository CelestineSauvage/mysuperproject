import sys
import logging
import argparse
from helpers.Chronometer import Chronometer
import datetime
from load import DataInsertion

ARG_PATH = "path"


def parse_args():
    # TODO add subparser for each data source

    parser = argparse.ArgumentParser(
        description='Load data into Db')
    parser.add_argument(f"--{ARG_PATH}", type=str,
                        help='directory where json files will be store')

    args = parser.parse_args()
    args_dict = vars(args)
    return args_dict


def main():
    chrono = Chronometer()

    args = parse_args()

    now = datetime.datetime.now(datetime.UTC)
    dt_string = now.strftime("%Y_%m_%d_%H_%M_%S")

    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(filename=f"logs/log_loadData_{dt_string}.log",
                        format=log_format, level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info("load_data_into_db")
    DataInsertion.load_to_db(args['path'])


if __name__ == "__main__":
    sys.exit(main())
