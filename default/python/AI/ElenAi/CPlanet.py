"""
This is a representation of a planet.
"""

from __future__ import print_function


class CPlanet(object):


    def __init__(self, ixPlanet, ixEmpire, iPlanetType, iHabitableSize, sSpecies, fPopulation, sSpecialFrozenset, sBuildingList):
        self.__m_ixPlanet = ixPlanet
        self.__m_ixEmpire = ixEmpire
        self.__m_iPlanetType = iPlanetType
        self.__m_iHabitableSize = iHabitableSize
        self.__m_sSpecies = sSpecies
        self.__m_fPopulation = fPopulation
        self.__m_sSpecialFrozenset = sSpecialFrozenset

        # The same building name can exist on one planet multiple times, for example BLD_TERRAFORM.

        self.__m_sBuildingList = sBuildingList

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
        return sBuilding in self.__m_sBuildingList


    def vSetSystem(self, oSystem):
        self.__m_oSystem = oSystem


    def oGetSystem(self):
        return self.__m_oSystem


    def vDump(self):
        if (self.bIsNative()):
            print(
                'Planet %d is a colony of native species \'%s\' (%.2f).' % (
                    self.ixGetPlanet(),
                    self.sGetSpecies(),
                    self.fGetPopulation()
                )
            )
        elif (self.bIsColony()):
            print(
                'Planet %d is a colony of species \'%s\' (%.2f) owned by empire %d.' % (
                    self.ixGetPlanet(),
                    self.sGetSpecies(),
                    self.fGetPopulation(),
                    self.ixGetEmpire()
                )
            )
        elif (self.bIsOutpost()):
            print(
                'Planet %d is an outpost owned by empire %d.' % (
                    self.ixGetPlanet(),
                    self.ixGetEmpire()
                )
            )
        elif (self.bIsColonisable()):
            print(
                'Planet %d can be colonised.' % (
                    self.ixGetPlanet()
                )
            )
        else:
            print(
                'Planet %d is in an invalid state!' % (
                    self.ixGetPlanet()
                )
            )
