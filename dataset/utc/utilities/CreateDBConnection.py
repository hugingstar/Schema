# -*- coding: utf-8 -*-

import psycopg2
import psycopg2.extras
import logging


class CreateDBConnection:
    """
    this class create a DB connection
    """
    def __init__(self, dbname, user, host, password):
        # Python 3 대응: 인스턴스별 유연한 로깅 계층 식별 및 내부 커넥션 초기화 분리
        self.__logger = logging.getLogger(__name__)
        self.__connection = None
        self.__initDBconnection(dbname, user, host, password)
    
    def getDBConnection(self):
        return self.__connection
        
    def __initDBconnection(self, dbname, user, host, password):
        self.__logger.info('establishing connection to DB %s', dbname)
        
        # Python 3 대응: 복잡한 문자열 결합 구조를 직관적이고 안전한 f-string 포맷으로 개조
        connection_param = f"dbname='{dbname}' user='{user}' host='{host}' password='{password}'"
        
        try:            
            self.__connection = psycopg2.connect(connection_param)
            self.__logger.info('connected to DB %s', dbname)
            return self.__connection
        except Exception as e:  # Python 3 대응: naked except 구문을 교정하고 상세 원인 로그 바인딩
            self.__logger.error('unable to connect to the database,\n please check if database %s is online', dbname)
            self.__logger.error('Database connection error details: %s', str(e))
            return None