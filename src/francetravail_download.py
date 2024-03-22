import sys
import os
import requests
import argparse
from pathlib import Path
from apiDataCollection.apiCallers.FranceEmploiApiCaller import \
    FranceEmploiApiCaller, DepartmentJobsCaller


def collect_from_france_emploi():
    france_emploi_client_id = os.environ.get("FRANCE_EMPLOI_CLIENT_ID", "")
    france_emploi_client_secret = os.environ.get(
        "FRANCE_EMPLOI_CLIENT_SECRET", "")
    print("Start of data collection for France Emploi")
    # Initialize the France Emploi API caller
    franceEmploi = FranceEmploiApiCaller(
        france_emploi_client_id, france_emploi_client_secret)

    # Authenticate to the France Emploi API services
    franceEmploi.authenticate("api_offresdemploiv2 o2dsoffre", {
        "realm": "/partenaire"})

    return franceEmploi


def download(kwargs):
    # Load credentials of API providers
    # TODO : change with DataCollector
    france_emploi = collect_from_france_emploi()

    directory = kwargs["path"]
    # create directory if doesn't exist
    Path(directory).mkdir(parents=True, exist_ok=True)

    if (kwargs["department"] is None):  # if department not specified
        int_departments = list(range(1, 96, 1))
        int_departments.remove(20)
        departments = [(f"{number:02d}") for number in int_departments]
        departments += ["971", "972", "973", "974", "976"]
    else:
        departments = [kwargs["department"]]

    kwargs.pop("department")
    kwargs.pop("path")

    try:
        for dep in departments:
            departement_download = DepartmentJobsCaller(
                france_emploi,
                path=directory,
                departement=dep,
                **kwargs)
            try:
                departement_download.get_jobs_by_department()
            except requests.exceptions.RequestException:
                pass
    except KeyboardInterrupt:  # SIG INT
        sys.exit()


def main():
    parser = argparse.ArgumentParser(
        description='Download jobs from France API in json files')
    parser.add_argument('path', type=str,
                        help='directory where json files will be store')
    parser.add_argument('--department',
                        help='specified department, if not, all departments are dl')
    parser.add_argument('--publieDepuis',
                        help="1, 3, 7, 14 or 31 last day(s)")

    args = parser.parse_args()
    args_dict = vars(args)
    download(args_dict)


if __name__ == "__main__":
    sys.exit(main())
