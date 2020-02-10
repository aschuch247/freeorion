"""
This is a representation of a planet.
"""


class CPlanet(object):


    def __init__(self, ixPlanet, sSpecies):
        self.__m_ixPlanet = ixPlanet
        self.__m_sSpecies = sSpecies

        self.__m_oSystem = None


    def ixGetPlanet(self):
        return self.__m_ixPlanet


    def sGetSpecies(self):
        """
        Return the name of the species. In case the planet is not inhabited, an empty string will be returned.
        """

        return self.__m_sSpecies


    def bIsColony(self):
        return self.__m_sSpecies != ''


    def bIsOutpost(self):
        return self.__m_sSpecies == ''


    def vSetSystem(self, oSystem):
        self.__m_oSystem = oSystem


    def oGetSystem(self):
        return self.__m_oSystem
