# -*- coding: utf-8 -*-
import json
import sys
import os
import logging
from inference.configuration.configuration import CONFIG
from collections import namedtuple


CONSTANTS = None
"""
this class defines constants used throughout the classification of points
and clusters
"""

path = CONFIG.CLASSIFIERCONSTANTS
__jsonData = {}
if not os.path.isfile(path):
    msg = "'" + path + "' doesn't exist"
    raise Exception(msg)

try:
    # Python 3 대응: 인코딩 명시 및 안전한 파일 오픈
    with open(path, 'r', encoding='utf-8') as json_config_file:
        __jsonData = json.load(json_config_file)
        # Python 3 대응: __jsonData.keys()를 list로 명시적 변환
        CONSTANTS = namedtuple('CONFIG', list(__jsonData.keys()))(**__jsonData)

except ValueError as error:
    logging.error('invalid json config file: ' + path)
    logging.error(str(error))  # Python 3 대응: error.message 대신 str(error) 사용
    sys.exit(0)
except OSError as error:  # Python 3 대응: IOError를 OSError로 변경
    logging.error('invalid json config file. wrong path: ' + path)
    logging.error(str(error))  # Python 3 대응: error.message 대신 str(error) 사용
    sys.exit(0)