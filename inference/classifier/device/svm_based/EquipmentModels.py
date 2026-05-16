# -*- coding: utf-8 -*-

from inference.classifier.device.svm_based.Util import Model


class Equipment(Model):
    """
    Standard Equipment Dictionary Models for SVM Features
    """
    def __init__(self):
        # Python 3 대응: super() 인자 선언 구문 간소화
        super().__init__()

        self.AHU = {
            "MixedAirTemp(AHU)": [['MA', 'T'], ['MA', 'TP'], ['MAT'], ['MIXED', 'AIR', 'TEMP'],
                                   ['AHU', 'MA', 'T'], ['AHU', 'MAT']],
            "MixedAirDamper(AHU)": [['MA', 'PS'], ['MA', 'P'], ['MA', 'POS'], ['MA', 'DMP'], ['MIXED', 'DAMPER', 'POSITION'],
                                     ['AHU', 'MA', 'PS'], ['AHU', 'MA', 'DAMP', 'POS']],
            "ReturnAirTemp(AHU)": [['RA', 'T'], ['RA', 'TP'], ['RAT'], ['RETURN', 'AIR', 'TEMP'],
                                   ['AHU', 'RA', 'T'], ['AHU', 'RETURN', 'TEMP']],
            "ReturnAirDamper(AHU)": [['RA', 'POS'], ['RA', 'DMP'], ['RA', 'PS'], ['RETURN', 'DAMPER', 'POSITION'],
                                      ['AHU', 'RA', 'POS'], ['AHU', 'RETURN', 'POS']],
            "OutdoorAirTemp(AHU)": [['OA', 'T'], ['OAT'], ['OUTDOOR', 'AIR', 'TEMP'],
                                    ['AHU', 'OA', 'T'], ['AHU', 'OUTDOOR', 'TEMP']],
            "Humidity(AHU)": [['RH'], ['HUM'], ['AIR', 'HUMIDITY'],
                              ['AHU', 'RH'], ['AHU', 'HUM']]
        }

        self.VAV = {
            "ZoneTemp(VAV)": [['ZN', 'T'], ['ZN', 'TEMP'], ['ZONE', 'TEMP'], ['ROOM', 'TEMP'],
                              ['VAV', 'ZN', 'T'], ['VAV', 'ZONE', 'TEMP']],
            "DamperPosition(VAV)": [['ZN', 'POS'], ['ZN', 'DMP'], ['ZN', 'PS'], ['ZONE', 'DAMPER'], ['ROOM', 'DAMPER'],
                                    ['VAV', 'ZN', 'POS'], ['VAV', 'ZONE', 'POS']],
            "SetPoint(VAV)": [['ZN', 'SP'], ['ZN', 'SET'], ['ZONE', 'SP'], ['SET', 'TEMP'], ['ROOM', 'SET', 'TEMP'],
                              ['VAV', 'ZN', 'SP'], ['VAV', 'ZONE', 'STP']],
            "Occupancy(VAV)": [['OCC'], ['OCCUPANCY'], ['OCCUPANT'], ['ROOM', 'OCC'],
                               ['VAV', 'OCC'], ['VAV', 'OCCUPANT']],
            "Humidity(VAV)": [['RH'], ['HUM'], ['AIR', 'HUMIDITY'], ['ZONE', 'HUMIDITY'], ['ROOM', 'HUMIDITY'],
                              ['VAV', 'RH'], ['VAV', 'HUM']]
        }

        self.VRF = {
            "ZoneTemp(VRF)": [['ZN', 'T'], ['ZN', 'TEMP'], ['ZONE', 'TEMP'], ['ROOM', 'TEMP'],
                              ['VRF', 'ZN', 'T'], ['VRF', 'ZN', 'T']],
            "OutdoorTemp(VRF)": [['OA', 'TEMP'], ['OAT'], ['OUT', 'TEMP'], ['ODR', 'TEMP'], ['OUTDOOR', 'TEMP'],
                                 ['VRF', 'OA', 'T'], ['VRF', 'OAT']],
            "SetPoint(VRF)": [['ZN', 'SP'], ['ZN', 'SET'], ['ZONE', 'SP'], ['SET', 'TEMP'], ['ROOM', 'SET', 'TEMP'],
                              ['VRF', 'ZN', 'SP'], ['VRF', 'RM', 'SP']],
            "Occupancy(VRF)": [['OCC'], ['OCCUPANCY'], ['OCCUPANT'], ['ROOM', 'OCC'],
                               ['VRF', 'OCC'], ['VRF', 'OCCUPANT']],
            "Humidity(VRF)": [['RH'], ['HUM'], ['AIR', 'HUMIDITY'], ['ZONE', 'HUMIDITY'], ['ROOM', 'HUMIDITY'],
                              ['VRF', 'RH'], ['VRF', 'HUM']]
        }