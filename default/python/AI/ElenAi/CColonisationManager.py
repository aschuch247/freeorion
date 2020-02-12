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
from ElenAi.CEmpireRelation import CEmpireRelation
from ElenAi.CManager import CManager


class CColonisationManager(CManager):


    def __init__(self, fo, oUniverse, oSpeciesData):
        super(CColonisationManager, self).__init__(fo)

        self.__m_oUniverse = oUniverse
        self.__m_oSpeciesData = oSpeciesData
        self.__m_oEmpireRelation = CEmpireRelation(self.fo.empireID())
        self.__m_oColonyPredictor = CColonyPredictor(self.fo.getEmpire().availableTechs)


    def vManage(self):
        self.__vAssertTargetPopulation()


    def tixGetUnownedSystem(self):
        """
        Return systems where all of the planets (at least one) are unowned.
        """

        oFoUniverse = self.fo.getUniverse()

        for ixSystem in oFoUniverse.systemIDs:
            oFoSystem = oFoUniverse.getSystem(ixSystem)

            if (not oFoSystem.planetIDs.empty()):
                bIsOwned = False

                for ixPlanet in oFoSystem.planetIDs:
                    oFoPlanet = oFoUniverse.getPlanet(ixPlanet)

                    if (not oFoPlanet.unowned):
                        bIsOwned = True
                        break

                if (not bIsOwned):
                    yield ixSystem


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
