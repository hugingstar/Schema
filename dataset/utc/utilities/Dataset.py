# -*- coding: utf-8 -*-

import psycopg2
import psycopg2.extras
import logging
import dataset.utc.utilities.Constants as Constants


class Point:
    """
    Represents a single data point in the building system
    """
    def __init__(self):
        self._pointName = ' '
        self.description = ' '
        self.object_type = ' '
        self.device_id = -1
        self.device_name = " "
        self.object_id = ' '
        self.program_name = ' '
        self.value = ' '

    @property
    def pointName(self):
        return self._pointName

    @pointName.setter
    def pointName(self, pointname):
        self._pointName = pointname

    def __eq__(self, other):
        if isinstance(other, Point):
            if (self.pointName == other.pointName and
                self.object_type == other.object_type and
                self.device_id == other.device_id and
                self.object_id == other.object_id):
                    return True
        return False

    def __hash__(self):
        return hash(self.pointName)


class Dataset:
    """
    data structure to hold data to be stored in the dataset table
    """
    def __init__(self):
        # Python 3 대응: 문자열 '__name__' 대신 로거 규칙에 맞게 __name__ 변수 적용
        self.__logger = logging.getLogger(__name__)
        self._dataPoints = []
        self._dataset_name = ''
        self.vendor = ''
        self.date = ''
        self.distributor = ' '
        self.site = ''

    def __len__(self):
        return len(self._dataPoints)

    @property
    def datasetName(self):
        return self._dataset_name

    @datasetName.setter
    def datasetName(self, value):
        self._dataset_name = value

    @property
    def dataPoints(self):
        return self._dataPoints

    @dataPoints.setter
    def dataPoints(self, value):
        self._dataPoints = value

    def writeDataSetToDB(self, dbconnection):
        dataset_id = -1
        cur = dbconnection.cursor()

        SQL = "INSERT INTO " + Constants.TABLE.INDEX_TABLE + " (dataset_name, vendor, date, distributor, site)" +\
              "VALUES (%s, %s, %s, %s, %s)"
        try:         
            cur.execute(SQL,
                        (self.datasetName,
                         self.vendor,
                         self.date, 
                         self.distributor, 
                         self.site ))
                         
            dbconnection.commit()
        except psycopg2.Error as e:
            dbconnection.rollback()
            print('something went wrong...')
            print(e.pgerror)
        
        # get dataset ID
        SQL = "SELECT dataset_id FROM " + Constants.TABLE.INDEX_TABLE + " WHERE  dataset_name='" + self.datasetName +\
              "' AND vendor='" + self.vendor + "' AND distributor='" + self.distributor + "' AND site='" +\
              self.site + "' LIMIT 1"
        print(SQL)  
        try:                  
            cur.execute(SQL)  
            dbconnection.commit()
            dataset_id = cur.fetchone()[0]
            print(dataset_id)
        except psycopg2.Error as e:
            dbconnection.rollback()
            print('something went wrong...')
            print(e.pgerror)
    
        SQL = "INSERT INTO " + Constants.TABLE.DATASET_TABLE +\
              " (point_name, description, object_type, device_id, device_name, object_id, program_name, value, dataset_id)"+\
              " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"        
        
        print(SQL)        
        
        for point in self.dataPoints:
            try:
                cur.execute(SQL,
                            (point.pointName,
                             point.description,
                             point.object_type,
                             point.device_id,
                             point.device_name,
                             point.object_id,
                             point.program_name,
                             point.value,
                             dataset_id
                             ))

                dbconnection.commit()
            except psycopg2.Error as e:
                dbconnection.rollback()
                print('something went wrong...')
                print(e.pgerror)

        cur.close()
        return True

    def addPoint(self, point):
        self.dataPoints.append(point)
        return True

    @property
    def numberOfPoints(self):
        return len(self.dataPoints)

    def __repr__(self):
        tmp = ''
        for point in self.dataPoints:
            tmp += point.pointName + '\n'
        return tmp

    def loadDatasetFromFile(self, filename):
        try:
            data_points_local = []
            # Python 3 대응: open 시 인코딩 명시
            with open(filename, 'r', encoding='utf-8') as datafile:
                lines = datafile.readlines()
                for line in lines:
                    line = line.strip()
                    parts = line.split(',')
                    if len(parts) == 1 and line:
                        point = Point()
                        point.pointName = line
                        data_points_local.append(point)
            
            self.datasetName = filename
            self.dataPoints = list(set(data_points_local))

            msg = 'Loaded dataset from ' + filename
            self.__logger.info(msg)
            return True, msg
        except OSError as e:  # Python 3 대응: IOError -> OSError
            msg = e.strerror + ' filename:"' + filename + '"'
            self.__logger.error(msg)
            return False, msg

    def __loadDataFromDB(self, dataset_id, dbconnection):
        cur = dbconnection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        data_points_local = []
        SQL = "SELECT * FROM " + Constants.TABLE.DATASET_TABLE +\
              " WHERE dataset_id='" + str(dataset_id) + "'"
        print(SQL)
        try:
            cur.execute(SQL)
            dbconnection.commit()
            self.datasetName = str(dataset_id)
            for record in cur:
                point = Point()
                point.pointName = record['point_name']
                point.description = record['description']
                point.object_type = record['object_type']
                point.device_id = record['device_id']
                point.device_name = record['device_name']
                # 버그 수정: 원본의 원치 않는 튜플 생성 trailing comma(,) 제거
                point.object_id = record['object_id']
                point.program_name = record['program_name']
                point.value = record['value']
                data_points_local.append(point)

            self.dataPoints = list(set(data_points_local))

        except psycopg2.Error as e:
            dbconnection.rollback()
            self.__logger.error(e.pgerror)
            # Python 3 대응: e.message 대신 str(e) 사용
            return False, str(e)

        cur.close()
        msg = 'Loaded dataset from DB' + str(dataset_id)
        return True, msg

    def loadDatasetFromDB(self, dataset_id, dbconnection):
        return self.__loadDataFromDB(dataset_id, dbconnection)

    def printPoints(self):
        for point in self.dataPoints:
            print(vars(point))