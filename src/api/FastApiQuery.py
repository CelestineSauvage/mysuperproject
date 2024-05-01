from unidecode import unidecode
import re
from fastapi import HTTPException, status
from .FastApiConstants import FastApiConstants


REGION_LIST = FastApiConstants.REGION_LIST.value


class JobQuery:

    def __init__(self, col_jobs, col_region) -> None:
        self.col_jobs = col_jobs
        self.col_region = col_region

    def _process_string(self, val: str):
        """_summary_

        Args:
            val (str): _description_

        Returns:
            _type_: _description_
        """
        val = unidecode(val)
        val = val.lower()  # lower case
        val = re.sub('[^0-9a-zA-Z]+', ' ', val)
        return val

    def _search_by_town(self, town: str):
        """_summary_

        Args:
            town (str): _description_

        Returns:
            _type_: _description_
        """
        p_town = self._process_string(town)
        return {"contents.place.town ": f"{p_town}"}

    def _search_by_department(self, dep: str):
        """_summary_

        Args:
            dep (str): _description_

        Returns:
            _type_: _description_
        """
        return {"contents.place.department": f"{dep}"}

    def _search_by_region(self, reg: str):
        """_summary_

        Args:
            reg (str): _description_

        Raises:
            HTTPException: _description_

        Returns:
            _type_: _description_
        """
        if reg not in REGION_LIST:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Region code must be in {REGION_LIST}."
            )
        result = list(self.col_region.aggregate([
            {"$match": {"region.code": f"{reg}"}}
        ]))
        deps = [x["code"] for x in result]
        return {"contents.place.department": {"$in": deps}}

    def department_list(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return list(self.col_region.aggregate([
            {
                "$project": {
                    "_id": 0,
                    "code": 1,
                    "libelle": 1
                }
            }
        ]))

    def region_list(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        result = list(self.col_region.aggregate([
            {
                "$project": {
                    "_id": 0,
                    "code": "$region.code",
                    "libelle": "$region.libelle"
                }
            }
        ]))
        return list({v['code']: v for v in result}.values())

    def query_groupby(self, groupby: str, number: str, limit=10, place: str = "dep"):
        """request to mongodb stat from department or region, groupby attribut

        Args:
            number (_type_): department number

        Returns:
            list: [{town1 : count1}, {town2 : count2} ... ]
        """
        if place == "reg":
            filter = self._search_by_region(number)
        else:
            filter = self._search_by_department(number)
        return list(self.col_jobs.aggregate([
            {"$match": filter},
            {"$group": {"_id": f'${groupby}', "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]))

    def search_string_in_department(self, title: str, number: str):
        """search

        Args:
            title (str): _description_
            number (str): _description_

        Returns:
            _type_: _description_
        """
        expr = re.compile(f"{self._process_string(title)}")
        return list(self.col_jobs.aggregate([
            {"$match": {
                "$and": [
                    self._search_by_department(number),
                    {
                        "$or": [
                            {"contents.title": expr},
                            {"contents.description": expr},
                            {"contents.category": expr}
                        ]}
                ]
            }}
        ]))
