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


    def __init__(self, fo, oUniverse, oEmpireManager, oEmpireRelation, oSpeciesData):
        super(CColonisationManager, self).__init__(fo)

        self.__m_oUniverse = oUniverse
        self.__m_oEmpireManager = oEmpireManager
        self.__m_oEmpireRelation = oEmpireRelation
        self.__m_oSpeciesData = oSpeciesData

        self.__m_oColonyPredictor = CColonyPredictor(self.fo.getEmpire().availableTechs)
        self.__m_listColonisation = self.__listCreateColonisation()

        print(self.__m_listColonisation)


    def vManage(self):
        self.__vAssertTargetPopulation()


    def __listCreateColonisation(self):
        listColonisation = []

        # Inside the empire area, where supply lines are present everywhere, prefer large planets first. At the border
        # of the empire, prefer small planets, in order to expand the supply area.

        # @todo Improve this!

        for oSystem in self.__m_oUniverse.toGetSystem():
            bIsOwnSystem = False
            PlanetTuple = (-1, -1, '', -1.0)

            for oPlanet in oSystem.toGetPlanet():
                if (self.__m_oEmpireRelation.bIsOwnPlanet(oPlanet)):
                    bIsOwnSystem = True
                elif (not oPlanet.bIsInhabited()):

                    # Exclude planets owned by natives or other empires.

                    for sSpecies in self.__m_oEmpireManager.sGetSpeciesFrozenset():
                        fMaxPopulation = self.__m_oColonyPredictor.fGetMaxPopulation(oPlanet, self.__m_oSpeciesData.oGetSpecies(sSpecies))

                        if (fMaxPopulation > PlanetTuple[3]):
                            PlanetTuple = (oSystem.ixGetSystem(), oPlanet.ixGetPlanet(), sSpecies, fMaxPopulation)

            if (PlanetTuple[3] > 0.0):

                # This planet can be colonised.
                # @todo If the system is already owned by us, it is better to build an outpost base!

                # print(
                #     'Planet %d can be colonised with species \'%s\' (%.2f).' % (
                #         PlanetTuple[1],
                #         PlanetTuple[2],
                #         PlanetTuple[3]
                #     )
                # )

                listColonisation.append(PlanetTuple)

        listColonisation.sort(key=lambda PlanetTuple: PlanetTuple[3], reverse=True)

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
