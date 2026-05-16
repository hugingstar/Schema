# -*- coding: utf-8 -*-

import json
import sys
import os
import logging
from collections import namedtuple


def __createFolders():
    """create folders if they don't exists"""
    if not os.path.exists(CONFIG.OUTPUTFOLDER):
        os.makedirs(CONFIG.OUTPUTFOLDER)

CONFIG_PATH = 'config'
CONFIG_FILE = 'config.json'
CONFIG = None

path = CONFIG_PATH + '/' + CONFIG_FILE
__jsonData = {}
if os.path.isfile(path):
    path = path
elif os.path.isfile('../' + CONFIG_PATH + '/' + CONFIG_FILE):
    path = '../' + CONFIG_PATH + '/' + CONFIG_FILE
elif os.path.isfile('inference/' + CONFIG_PATH + '/' + CONFIG_FILE):
    path = 'inference/' + CONFIG_PATH + '/' + CONFIG_FILE

try:
    # Python 3 대응: 인코딩 명시 및 안전한 파일 오픈
    with open(path, 'r', encoding='utf-8') as json_config_file:
        __jsonData = json.load(json_config_file)
        # Python 3 대응: __jsonData.keys()를 list로 명시적 변환
        CONFIG = namedtuple('CONFIG', list(__jsonData.keys()))(**__jsonData)
        __createFolders()

except ValueError as error:
    logging.error('invalid json config file: ' + path)
    logging.error(str(error))  # Python 3 대응: error.message 대신 str(error) 사용
    sys.exit(0)
except OSError as error:  # Python 3 대응: IOError를 OSError로 변경
    logging.error('invalid json config file. wrong path: ' + path)
    logging.error(str(error))  # Python 3 대응: error.message 대신 str(error) 사용
    sys.exit(0)