"""
The colonisation manager assesses the universe for habitable planets.
"""

# @todo We need a method to rate planets based on the system and the planet itself.


from ElenAi.CManager import CManager


class CColonisationManager(CManager):


    def __init__(self, fo):
        super(CColonisationManager, self).__init__(fo)


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


    def fGetMaxPopulation(self, oFoPlanet, sSpecies):
        return 0.0


    def __vAssertTargetPopulation(self):
        oFoUniverse = self.fo.getUniverse()

        for ixPlanet in oFoUniverse.planetIDs:
            oFoPlanet = oFoUniverse.getPlanet(ixPlanet)

            if (self._bIsOwn(oFoPlanet)):
                fActualMaxPopulation = oFoPlanet.initialMeterValue(self.fo.meterType.targetPopulation)
                fExpectedMaxPopulation = self.fGetMaxPopulation(oFoPlanet, oFoPlanet.speciesName)

                if (fActualMaxPopulation != fExpectedMaxPopulation):
                    print 'Actual maximum population %.2f differs from expected maximum population %.2f for planet %d!' % (
                        fActualMaxPopulation,
                        fExpectedMaxPopulation,
                        ixPlanet
                    )
