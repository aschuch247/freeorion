"""
This is a species data provider (with static data).
"""


class CSpeciesDataStatic(object):


    def __init__(self):
        self.__dictSpecies = dict()


    def vAddSpecies(self, oSpecies):
        self.__dictSpecies[oSpecies.sGetName()] = oSpecies


    def oGetSpecies(self, sName):
        return self.__dictSpecies[sName]
