"""
This is a representation of a planet.
"""


class CPlanet(object):


    def __init__(self, ixPlanet, ixEmpire, sSpecies, fPopulation):
        self.__m_ixPlanet = ixPlanet
        self.__m_ixEmpire = ixEmpire
        self.__m_sSpecies = sSpecies
        self.__m_fPopulation = fPopulation

        self.__m_oSystem = None


    def ixGetPlanet(self):
        return self.__m_ixPlanet


    def ixGetEmpire(self):
        """
        Return the empire that owns the planet. The value can be negative in case the planet is not owned by any empire.
        The empire identifier 0 seems to be unused.
        """
        return self.__m_ixEmpire


    def sGetSpecies(self):
        """
        Return the name of the species. In case the planet is not inhabited, an empty string is returned.
        """

        return self.__m_sSpecies


    def fGetPopulation(self):
        return self.__m_fPopulation


    def bIsNative(self):
        """
        Indicate whether the planet is inhabited by natives.
        """

        return (self.__m_ixEmpire < 0) and (self.__m_sSpecies != '')


    def bIsColony(self):
        return (self.__m_ixEmpire >= 0) and (self.__m_sSpecies != '')


    def bIsOutpost(self):
        return (self.__m_ixEmpire >= 0) and (self.__m_sSpecies == '')


    def vSetSystem(self, oSystem):
        self.__m_oSystem = oSystem


    def oGetSystem(self):
        return self.__m_oSystem
