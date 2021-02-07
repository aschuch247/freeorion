"""
This is a database for ship hulls.
"""

from __future__ import print_function


class CShipHull(object):


    def __init__(self):
        self.__m_dictHull = {
            'SH_ASTEROID': {
                'detection': 25.0,
                'fuel': 1.0,
                'speed': 60.0,
                'stealth': 5.0,
                'structure': 30.0
            },
            'SH_BASIC_MEDIUM': {
                'detection': 25.0,
                'fuel': 3.0,
                'speed': 60.0,
                'stealth': 5.0,
                'structure': 10.0
            },
            'SH_BASIC_SMALL': {
                'detection': 25.0,
                'fuel': 8.0,
                'speed': 75.0,
                'stealth': 5.0,
                'structure': 5.0
            },
            'SH_DAMPENING_CLOUD_BODY': {
                'detection': 0.0,
                'fuel': 1.0,
                'speed': 20.0,
                'stealth': 45.0,
                'structure': 5000.0
            },
            'SH_DRONE_BODY': {
                'detection': 30.0,
                'fuel': 3.0,
                'speed': 30.0,
                'stealth': 5.0,
                'structure': 10.0
            },
            'SH_FLOATER_BODY': {
                'detection': 30.0,
                'fuel': 3.0,
                'speed': 20.0,
                'stealth': 15.0,
                'structure': 20.0
            },
            'SH_GUARD_0_BODY': {
                'detection': 10.0,
                'fuel': 0.0,
                'speed': 0.0,
                'stealth': 5.0,
                'structure': 25.0
            },
            'SH_GUARD_1_BODY': {
                'detection': 20.0,
                'fuel': 0.0,
                'speed': 0.0,
                'stealth': 5.0,
                'structure': 35.0
            },
            'SH_GUARD_MONSTER_BODY': {
                # 'detection'
                'fuel': 0.0,
                'speed': 0.0,
                'stealth': 5.0,
                'structure': 35.0
            },
            'SH_JUGGERNAUT_1_BODY': {
                'detection': 30.0,
                'fuel': 3.0,
                'speed': 30.0,
                'stealth': 5.0,
                'structure': 30.0
            },
            'SH_KRILL_1_BODY': {
                'detection': 10.0,
                'fuel': 5.0,
                'speed': 30.0,
                'stealth': 15.0,
                'structure': 20.0
            },
            'SH_KRILL_2_BODY': {
                'detection': 30.0,
                'fuel': 6.0,
                'speed': 30.0,
                'stealth': 15.0,
                'structure': 40.0
            },
            'SH_ROBOTIC': {
                'detection': 25.0,
                'fuel': 2.0,
                'speed': 75.0,
                'stealth': 5.0,
                'structure': 25.0
            }
        }


    def __dictGetSingleHull(self, sHull):
        dictSingleHull = self.__m_dictHull.get(sHull, None)

        if (dictSingleHull is None):
            dictSingleHull = dict()

            print('Ship hull \'%s\' is unknown!' % sHull)

        return dictSingleHull


    def fGetDetection(self, sHull):
        dictSingleHull = self.__dictGetSingleHull(sHull)

        return dictSingleHull.get('detection', 0.0)


    def fGetFuel(self, sHull):
        dictSingleHull = self.__dictGetSingleHull(sHull)

        return dictSingleHull.get('fuel', 0.0)


    def fGetSpeed(self, sHull):
        dictSingleHull = self.__dictGetSingleHull(sHull)

        return dictSingleHull.get('speed', 0.0)


    def fGetStealth(self, sHull):
        dictSingleHull = self.__dictGetSingleHull(sHull)

        return dictSingleHull.get('stealth', 0.0)


    def fGetStructure(self, sHull):
        dictSingleHull = self.__dictGetSingleHull(sHull)

        return dictSingleHull.get('structure', 0.0)
