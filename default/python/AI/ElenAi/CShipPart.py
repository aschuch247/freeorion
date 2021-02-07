"""
This is a database for ship parts.
"""

from __future__ import print_function

from ElenAi.Constant.CShipPartClass import CShipPartClass


class CShipPart(object):


    def __init__(self):
        self.__m_dictPart = {
            'AR_DIAMOND_PLATE': {
                'partClass': CShipPartClass.armour,
                'capacity': 18.0
            },
            'AR_NEUTRONIUM_PLATE': {
                'partClass': CShipPartClass.armour,
                'capacity': 40.0
            },
            'AR_PRECURSOR_PLATE': {
                'partClass': CShipPartClass.armour,
                'capacity': 400.0
            },
            'AR_STD_PLATE': {
                'partClass': CShipPartClass.armour,
                'capacity': 6.0
            },
            'AR_XENTRONIUM_PLATE': {
                'partClass': CShipPartClass.armour,
                'capacity': 30.0
            },
            'AR_ZORTRIUM_PLATE': {
                'partClass': CShipPartClass.armour,
                'capacity': 11.0
            },
            'DT_DETECTOR_1': {
                'partClass': CShipPartClass.detection,
                'capacity': 25.0
            },
            'DT_DETECTOR_2': {
                'partClass': CShipPartClass.detection,
                'capacity': 75.0
            },
            'FU_IMPROVED_ENGINE_COUPLINGS': {
                'partClass': CShipPartClass.speed,
                'capacity': 20.0
            },
            'SH_DEFENSE_GRID': {
                'partClass': CShipPartClass.shields,
                'capacity': 3.0
            },
            'SH_DEFLECTOR': {
                'partClass': CShipPartClass.shields,
                'capacity': 5.0
            },
            'SR_JAWS': {
                'partClass': CShipPartClass.shortRange,
                'damage': 5.0
            },
            'SR_PLASMA_DISCHARGE': {
                'partClass': CShipPartClass.shortRange,
                'damage': 20.0
            },
            'SR_WEAPON_0_1': {
                'partClass': CShipPartClass.shortRange,
                'damage': 1.0,
                'shots': 3
            },
            'SR_WEAPON_1_1': {
                'partClass': CShipPartClass.shortRange,
                'damage': 3.0
            },
            'SR_WEAPON_2_1': {
                'partClass': CShipPartClass.shortRange,
                'damage': 5.0
            },
            'SR_WEAPON_3_1': {
                'partClass': CShipPartClass.shortRange,
                'damage': 9.0
            },
            'SR_WEAPON_4_1': {
                'partClass': CShipPartClass.shortRange,
                'damage': 15.0
            }
        }


    def __dictGetSinglePart(self, sPart):
        dictSinglePart = self.__m_dictPart.get(sPart, None)

        if (dictSinglePart is None):
            dictSinglePart = dict()

            print('Ship part \'%s\' is unknown!' % sPart)

        return dictSinglePart


    def fGetDamage(self, sPart):
        dictSinglePart = self.__dictGetSinglePart(sPart)

        return dictSinglePart.get('shots', 1) * dictSinglePart.get('damage', 0.0)


    def fGetDetection(self, sPart):
        dictSinglePart = self.__dictGetSinglePart(sPart)

        if (dictSinglePart.get('partClass') != CShipPartClass.detection):
            return 0.0

        return dictSinglePart.get('capacity', 0.0)


    def fGetShield(self, sPart):
        dictSinglePart = self.__dictGetSinglePart(sPart)

        if (dictSinglePart.get('partClass') != CShipPartClass.shields):
            return 0.0

        return dictSinglePart.get('capacity', 0.0)


    def fGetSpeed(self, sPart):
        dictSinglePart = self.__dictGetSinglePart(sPart)

        if (dictSinglePart.get('partClass') != CShipPartClass.speed):
            return 0.0

        return dictSinglePart.get('capacity', 0.0)


    def fGetStructure(self, sPart):
        dictSinglePart = self.__dictGetSinglePart(sPart)

        if (dictSinglePart.get('partClass') != CShipPartClass.armour):
            return 0.0

        return dictSinglePart.get('capacity', 0.0)
