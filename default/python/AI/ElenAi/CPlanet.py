"""
This is a representation of a planet.
"""


class CPlanet(object):


    def __init__(self, ixPlanet, ixEmpire, iPlanetType, iHabitableSize, sSpecies, fPopulation, sSpecialFrozenset, sBuildingFrozenset):
        self.__m_ixPlanet = ixPlanet
        self.__m_ixEmpire = ixEmpire
        self.__m_iPlanetType = iPlanetType
        self.__m_iHabitableSize = iHabitableSize
        self.__m_sSpecies = sSpecies
        self.__m_fPopulation = fPopulation
        self.__m_sSpecialFrozenset = sSpecialFrozenset
        self.__m_sBuildingFrozenset = sBuildingFrozenset

        self.__m_oSystem = None


    def ixGetPlanet(self):
        return self.__m_ixPlanet


    def ixGetEmpire(self):
        """
        Return the empire that owns the planet. The value can be negative in case the planet is not owned by any empire.
        The empire identifier 0 seems to be unused.
        """
        return self.__m_ixEmpire


    def bIsOwned(self):
        """
        Return whether the planet is owned by any empire.
        """

        return self.__m_ixEmpire >= 0


    def iGetPlanetType(self):
        return self.__m_iPlanetType


    def iGetHabitableSize(self):
        return self.__m_iHabitableSize


    def sGetSpecies(self):
        """
        Return the name of the species. In case the planet is not inhabited, an empty string is returned.
        """

        return self.__m_sSpecies


    def bIsInhabited(self):
        return self.__m_sSpecies != ''


    def fGetPopulation(self):
        return self.__m_fPopulation


    def bIsNative(self):
        """
        Indicate whether the planet is inhabited by natives.
        """

        return (not self.bIsOwned()) and (self.bIsInhabited())


    def bIsColony(self):
        return (self.bIsOwned()) and (self.bIsInhabited())


    def bIsOutpost(self):
        return (self.bIsOwned()) and (not self.bIsInhabited())


    def bIsColonisable(self):
        return (not self.bIsOwned()) and (not self.bIsInhabited())


    def bHasSpecial(self, sSpecial):
        return sSpecial in self.__m_sSpecialFrozenset


    def bHasBuilding(self, sBuilding):
        return sBuilding in self.__m_sBuildingFrozenset


    def vSetSystem(self, oSystem):
        self.__m_oSystem = oSystem


    def oGetSystem(self):
        return self.__m_oSystem