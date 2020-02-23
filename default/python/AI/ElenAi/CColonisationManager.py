"""
The colonisation manager assesses the universe for habitable planets.
"""

# @todo We need a method to rate planets based on the system and the planet itself.
# - Prefer systems with many planets for easier defence.
# - Prefer systems with black hole or red star (can be converted to black hole) for ship production and the black hole
#   power generator. Also for better research.
# - Consider neutron stars for better research and BLD_NEUTRONIUM_EXTRACTOR.
# - Consider white and blue stars for PHOTOTROPHIC species.

from __future__ import print_function

from ElenAi.CColonyPredictor import CColonyPredictor
from ElenAi.CManager import CManager


class CColonisationManager(CManager):


    def __init__(self, fo, oUniverse, oEmpireManager, oEmpireRelation, oColonyPredictor, oSpeciesData):
        super(CColonisationManager, self).__init__(fo)

        self.__m_oUniverse = oUniverse
        self.__m_oEmpireManager = oEmpireManager
        self.__m_oEmpireRelation = oEmpireRelation
        self.__m_oColonyPredictor = oColonyPredictor
        self.__m_oSpeciesData = oSpeciesData

        self.__m_dictColonisationOption = self.__dictCreateColonisationOption()
        self.__m_listColonisation = self.__listCreateColonisation(self.__m_dictColonisationOption)

        # print(self.__m_listColonisation)


    def vManage(self):
        self.__vAssertTargetPopulation()


    def tupleGetHigherPopulationColonisation(self, tupleColonisation1, tupleColonisation2):
        """
        Return the colonisation tuple with the highest population. But consider any species to have a higher population
        than SP_EXOBOT.
        """
        if (tupleColonisation1[2] == tupleColonisation2[2]):
            if (tupleColonisation1[3] >= tupleColonisation2[3]):
                return tupleColonisation1

            return tupleColonisation2
        else:
            if (tupleColonisation1[2] == 'SP_EXOBOT'):
                return tupleColonisation2

            if (tupleColonisation2[2] == 'SP_EXOBOT'):
                return tupleColonisation1

            if (tupleColonisation1[3] >= tupleColonisation2[3]):
                return tupleColonisation1

            return tupleColonisation2


    def tupleGetHighestPopulationColonisation(self, ixSystem, ixPlanet, dictPlanet = None):
        """
        If a planet can be colonised by multiple species, return the one with the highest population.
        """
        if (dictPlanet is None):
            dictPlanet = self.__m_dictColonisationOption[ixSystem][ixPlanet]

        tupleColonisation = tuple([-1, -1, 'SP_EXOBOT', -1.0])

        for sSpecies, tupleColonisationDetail in dictPlanet.items():
            tupleColonisation = self.tupleGetHigherPopulationColonisation(
                tupleColonisation,
                tuple([ixSystem, ixPlanet, sSpecies, tupleColonisationDetail[0]])
            )

        return tupleColonisation


    def tupleGetHighestPopulationBySystemColonisation(self, ixSystem):
        """
        Get the colonisation tuple with the best colony. 'None' in case the system cannot be colonised.
        """
        tupleColonisation = tuple([-1, -1, 'SP_EXOBOT', -1.0])
        dictSystem = self.__m_dictColonisationOption.get(ixSystem, dict())

        for ixPlanet, dictPlanet in dictSystem.items():
            oPlanet = self.__m_oUniverse.oGetSystem(ixSystem).oGetPlanet(ixPlanet)

            # For targeting planets for colonisation, only consider unowned planets. Native planets are inhabited,
            # so these planets are not included in dictColonisationOption.

            if (not oPlanet.bIsOwned()):
                tupleColonisation = self.tupleGetHigherPopulationColonisation(
                    tupleColonisation,
                    self.tupleGetHighestPopulationColonisation(ixSystem, ixPlanet, dictPlanet)
                )

        if (tupleColonisation[3] > 0.0):
            return tupleColonisation

        return None


    def __dictCreateColonisationOption(self):
        """
        Create a dictionary of colonisable planets. This dictionary contains all known not inhabited planets. This
        includes own outposts, other outposts and unowned planets.
        """
        dictColonisationOption = dict()

        for oSystem in self.__m_oUniverse.toGetSystem():
            for oPlanet in oSystem.toGetPlanet():
                if (not oPlanet.bIsInhabited()):
                    for sSpecies in self.__m_oEmpireManager.sGetSpeciesFrozenset():
                        fMaxPopulation = self.__m_oColonyPredictor.fGetMaxPopulation(oPlanet, self.__m_oSpeciesData.oGetSpecies(sSpecies))

                        if (fMaxPopulation > 0.0):

                            # This planet can be colonised.
                            # @todo If the system is already owned by us, it is better to build an outpost base!

                            # print(
                            #     'Planet %d can be colonised with species \'%s\' (%.2f).' % (
                            #         oPlanet.ixGetPlanet(),
                            #         sSpecies,
                            #         fMaxPopulation
                            #     )
                            # )

                            dictSystem = dictColonisationOption.get(oSystem.ixGetSystem(), dict())
                            dictPlanet = dictSystem.get(oPlanet.ixGetPlanet(), dict())

                            dictPlanet[sSpecies] = tuple([fMaxPopulation])

                            dictSystem[oPlanet.ixGetPlanet()] = dictPlanet
                            dictColonisationOption[oSystem.ixGetSystem()] = dictSystem

        return dictColonisationOption


    def dictGetColonisationOption(self):
        return self.__m_dictColonisationOption


    def __listCreateColonisation(self, dictColonisationOption):
        """
        Get a sorted (prioritised) list of unowned and uninhabited planets. This list is supposted to be used to get
        targets for outpost or colony ships.
        """

        # Inside the empire area, where supply lines are present everywhere, prefer large planets first. At the border
        # of the empire, prefer small planets, in order to expand the supply area.

        # @todo Improve this!
        # @todo Only colonise the first planet per system using an outpost ship, colonise further using outpost bases.
        # @todo Systems with only gas planets also need to be considered, at last when BLD_ART_PARADISE_PLANET is
        # available!
        # @todo Consider building outposts to increase the supply range and reach more planets!

        listColonisation = []

        for ixSystem in dictColonisationOption:
            tupleColonisation = self.tupleGetHighestPopulationBySystemColonisation(ixSystem)

            if (tupleColonisation is not None):
                listColonisation.append(tupleColonisation)

        listColonisation.sort(key=lambda tupleColonisation: tupleColonisation[3], reverse=True)

        return listColonisation


    def listGetColonisation(self):
        return self.__m_listColonisation


    def __vAssertTargetPopulation(self):
        for oSystem in self.__m_oUniverse.toGetSystem():
            for oPlanet in oSystem.toGetPlanet():
                if (self.__m_oEmpireRelation.bIsOwnPlanet(oPlanet)):
                    if (oPlanet.bIsOutpost()):
                        print('Planet %d is an outpost.' % (oPlanet.ixGetPlanet()))
                    elif (oPlanet.bIsColony()):
                        fActualMaxPopulation = self.fo.getUniverse().getPlanet(oPlanet.ixGetPlanet()).currentMeterValue(self.fo.meterType.targetPopulation)
                        fExpectedMaxPopulation = self.__m_oColonyPredictor.fGetMaxPopulation(oPlanet, self.__m_oSpeciesData.oGetSpecies(oPlanet.sGetSpecies()))

                        if (fActualMaxPopulation != fExpectedMaxPopulation):
                            print(
                                'Actual maximum population %.2f differs from expected maximum population %.2f for planet %d!' % (
                                    fActualMaxPopulation,
                                    fExpectedMaxPopulation,
                                    oPlanet.ixGetPlanet()
                                )
                            )

                            self.__m_oColonyPredictor.fGetMaxPopulation(oPlanet, self.__m_oSpeciesData.oGetSpecies(oPlanet.sGetSpecies()), True)
