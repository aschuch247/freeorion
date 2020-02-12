"""
This is a representation of a species.
"""


class CSpecies(object):


    def __init__(self, sName, dictPlanetTypePlanetEnvironment, sTagFrozenset, ixHomePlanetFrozenset):
        self.__m_sName = sName
        self.__m_dictPlanetTypePlanetEnvironment = dictPlanetTypePlanetEnvironment
        self.__m_sTagFrozenset = sTagFrozenset
        self.__m_ixHomePlanetFrozenset = ixHomePlanetFrozenset


    def sGetName(self):
        return self.__m_sName


    def iGetPlanetEnvironment(self, iPlanetType):
        return self.__m_dictPlanetTypePlanetEnvironment[iPlanetType]


    def bHasTag(self, sTag):
        return sTag in self.__m_sTagFrozenset


    def ixGetHomePlanetFrozenset(self):
        return self.__m_ixHomePlanetFrozenset


    def bIsHomePlanet(self, ixPlanet):
        return ixPlanet in self.__m_ixHomePlanetFrozenset
