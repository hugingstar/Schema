# -*- coding: utf-8 -*-

import sys

from dataset.utc.utilities import Dataset
from dataset.utc.utilities import Constants
from dataset.utc.utilities import CreateDBConnection


class DatasetParser:
    """
    this class encapsulates all the functionalities needed to parse a point
    dataset and produce tagged points in output
    """
    conn = None
    cursor = None

    def __init__(self):
        connector = CreateDBConnection.CreateDBConnection(
            Constants.CONNECTION.DB,
            Constants.CONNECTION.DBUSER,
            Constants.CONNECTION.HOST,
            Constants.CONNECTION.PASSWD
        )
        self.conn = connector.getDBConnection()
        if self.conn is not None:
            print('connection to DB established. Starting...')
        else:
            sys.exit(1)

    def loadBACnetNetworkPointDB(self, datasetID=1):
        dataset = Dataset.Dataset()
        dataset.loadDatasetFromDB(datasetID, self.conn)
        return dataset