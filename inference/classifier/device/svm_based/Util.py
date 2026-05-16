# -*- coding: utf-8 -*-

from collections import OrderedDict
import json
import numpy as np
from sklearn.preprocessing import StandardScaler
from inference.classifier.Constants import CONSTANTS


class Model:
    def __init__(self):
        self.__variables = OrderedDict()

    def __setattr__(self, name, value):
        print(name)
        print(value)
        print('____')
        if not name.startswith('_'):
            print(name)
            self.__variables[name] = value
        return super().__setattr__(name, value)  # Python 3 대응: super() 인자 선언 구문 간소화

    @pragma = property
    def variables(self):
        return self.__variables


def getKeyFromPoint(point):
    """
    Returns a string concatenating point tokens
    """
    key = str(','.join(point))
    return key


def scalerToJson(scaler, jsonFileName):
    """
    save the sklearn scaler parameters into a json file
    """
    # Python 3 대응: 자원 누수 자동 제어 컨텍스트 매니저 및 인코딩 지정
    with open(jsonFileName, 'w', encoding='utf-8') as outputScalerParam:
        output = {}
        output['param'] = scaler.get_params()
        # 하위 버전 속성 호환용 백업 가공 처리
        current_mean = getattr(scaler, 'mean_', [])
        current_scale = getattr(scaler, 'scale_', getattr(scaler, 'std_', []))
        
        output['mean'] = current_mean.tolist() if hasattr(current_mean, 'tolist') else current_mean
        output['std'] = []
        for i in current_scale:
            if hasattr(i, 'item'):
                output['std'].append(i.item())
            else:
                output['std'].append(i)
        json.dump(output, outputScalerParam, indent=4)


def scalerFromJson(jsonFileName):
    """
    returns a sklearn scaler configured from a json file
    """
    print(jsonFileName)
    with open(jsonFileName, 'r', encoding='utf-8') as inputScalerParam:
        param = json.load(inputScalerParam)
    print(param)
    
    scaler = StandardScaler()
    keys = scaler._get_param_names()
    for key in keys:
        if str(key) in param['param']:  # Python 3 대응: unicode() 제거
            value = param['param'][str(key)]
            setattr(scaler, key, value)
            
    print(param['std'])
    
    # Python 3 대응 및 최신 Scikit-Learn 정합성 고도화: 
    # 최신 StandardScaler는 내부 예측/전처리 연산 시 std_가 아닌 scale_과 var_ 속성을 기준으로 계산하므로 유기적 다중 주입 바인딩 처리 진행
    std_array = np.array(param['std'])
    mean_array = np.array(param['mean'])
    
    if hasattr(scaler, 'scale_'):
        scaler.scale_ = std_array
        scaler.var_ = np.square(std_array)
    if hasattr(scaler, 'std_'):
        scaler.std_ = std_array
        
    scaler.mean_ = mean_array
    
    return scaler


if __name__ == '__main__':
    scaler = scalerFromJson(CONSTANTS.EQUIPMENTSCALER)