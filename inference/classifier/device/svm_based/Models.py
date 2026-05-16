# -*- coding: utf-8 -*-

from collections import OrderedDict
import copy

from inference.classifier.device.svm_based.EquipmentModels import Equipment
from inference.classifier.device.svm_based.PointModels import Points


def singleton(cls):
    instance = cls()
    instance.__call__ = lambda: instance
    return instance


@singleton
class SVMModels:
    """this class holds models for equipment, points and support vectors
    """
    def __init__(self):
        self.__equipmentModels = None
        self.__eqpmntPntModels = None

    @property
    def EQUIPMENT_MODELS(self):
        if self.__equipmentModels is None:
            self.__equipmentModels = self.__getVarsInMdl(Equipment)
        return self.__equipmentModels

    @property
    def EQUIPMENTPOINT_MODELS(self):
        if self.__eqpmntPntModels is None:
            self.__eqpmntPntModels = self.__getVarsInMdl(Points,
                                                         self.EQUIPMENT_MODELS)
        return self.__eqpmntPntModels

    def __getVarsInMdl(self, classModel, others=None):
        """
        get the list of variables defined in a module
        """
        tmp = classModel()
        variables = OrderedDict()
        if others is not None:
            for key in others:
                variables[key] = copy.deepcopy(others[key])
                
        # Python 3 대응: iteritems() -> items() 변경
        for key, value in tmp.variables.items():
            if key not in variables:
                variables[key] = value
            else:
                for newKey in value:
                    if newKey in variables[key]:
                        variables[key][newKey].append(value[newKey])
                    else:
                        variables[key][newKey] = value[newKey]
        return variables

    @property
    def EQUIPMENTLABELS(self):
        """returns a list of all the equipment labels as list of strings"""
        # Python 3 대응: dict_keys 뷰 객체를 명시적 list로 반환하여 하위 호환성 보장
        return list(self.EQUIPMENT_MODELS.keys())

    @property
    def POINTLABELS(self):
        """returns a list of all the equipment labels as list of strings"""
        tmp = []
        for key in self.EQUIPMENT_MODELS:
            # Python 3 대응: dict_keys 뷰 객체를 명시적 list로 변환 후 확장
            tmp.extend(list(self.EQUIPMENTPOINT_MODELS[key].keys()))
        return tmp


if __name__ == '__main__':
    test = SVMModels()