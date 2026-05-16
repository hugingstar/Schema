# -*- coding: utf-8 -*-

from inference.classifier.device.svm_based.Util import Model


class Points(Model):
    """
    Standard Point Dictionary Models for SVM Features
    """
    def __init__(self):
        # Python 3 대응: super() 인자 선언 구문 간소화
        super().__init__()

        self.AHU = {}
        self.AHU['MixedAirTemp(AHU)'] = [['MA', 'T'], ['MA', 'TP'], ['MAT'],
                                         ['AHU', 'MA', 'T'], ['AHU', 'MAT']]
        self.AHU['MixedAirDamper(AHU)'] = [['MA', 'PS'], ['MA', 'P'], ['MA', 'POS'], ['MA', 'DMP'],
                                           ['AHU', 'MA', 'PS'], ['AHU', 'MA', 'DAMP', 'POS']]
        self.AHU['ReturnAirTemp(AHU)'] = [['RA', 'T'], ['RA', 'TP'], ['RAT'],
                                          ['AHU', 'RA', 'T'], ['AHU', 'RETURN', 'TEMP']]
        self.AHU['ReturnAirDamper(AHU)'] = [['RA', 'POS'], ['RA', 'DMP'], ['RA', 'PS'],
                                            ['AHU', 'RA', 'POS'], ['AHU', 'RETURN', 'POS']]
        self.AHU['OutdoorAirTemp(AHU)'] = [['OA', 'T'], ['OAT'],
                                           ['AHU', 'OA', 'T'], ['AHU', 'OUTDOOR', 'TEMP']]
        self.AHU['Humidity(AHU)'] = [['RA', 'H'], ['HUM'],
                                     ['AHU', 'RH'], ['AHU', 'HUM']]

        self.VAV = {}
        self.VAV['ZoneTemp(VAV)'] = [['ZN', 'T'], ['ZN', 'TEMP'], ['ZONE', 'TEMP'],
                                     ['VAV', 'ZN', 'T'], ['VAV', 'ZONE', 'TEMP']]
        self.VAV['DamperPosition(VAV)'] = [['ZN', 'POS'], ['ZN', 'DMP'], ['ZN', 'PS'],
                                           ['VAV', 'ZN', 'POS'], ['VAV', 'ZONE', 'POS']]
        self.VAV['SetPoint(VAV)'] = [['ZN', 'SP'], ['ZN', 'SET'], ['ZONE', 'SP'],
                                     ['VAV', 'ZN', 'SP'], ['VAV', 'ZONE', 'STP']]
        self.VAV['Occupancy(VAV)'] = [['OCC'], ['OCCPANCY'],
                                      ['VAV', 'OCC'], ['VAV', 'OCCUPANT']]
        self.VAV['Humidity(VAV)'] = [['RH'], ['HUM'],
                                     ['VAV', 'RH'], ['VAV', 'HUM']]

        self.VRF = {}
        self.VRF['ZoneTemp(VRF)'] = [['ZN', 'T'], ['ZN', 'TEMP'], ['ZONE', 'TEMP'], ['ROOM', 'TEMP'],
                                     ['ODU', 'ZN', 'T'], ['ODU', 'ZN', 'T']]
        self.VRF['OutdoorTemp(VRF)'] = [['OA', 'TEMP'], ['OAT'], ['OUT', 'TEMP'], ['ODR', 'TEMP'], ['OUTDOOR', 'TEMP'],
                                        ['VRF', 'OA', 'T'], ['VRF', 'OAT']]
        self.VRF['SetPoint(VRF)'] = [['ZN', 'SP'], ['ZN', 'SET'], ['ZONE', 'SP'], ['SET', 'TEMP'], ['ROOM', 'SET', 'TEMP'],
                                     ['VRF', 'ZN', 'SP'], ['VRF', 'RM', 'SP']]
        self.VRF['Occupancy(VRF)'] = [['OCC'], ['OCCUPANCY'], ['OCCUPANT'], ['ROOM', 'OCC'],
                                      ['VRF', 'OCC'], ['VRF', 'OCCUPANT']]
        self.VRF['Humidity(VRF)'] = [['RH'], ['HUM'], ['AIR', 'HUMIDITY'], ['ZONE', 'HUMIDITY'], ['ROOM', 'HUMIDITY'],
                                     ['VRF', 'RH'], ['VRF', 'HUM']]