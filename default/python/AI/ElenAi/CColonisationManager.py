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


    def bPlanetHasBuilding(self, oFoPlanet, sBuilding):
        for ixBuilding in oFoPlanet.buildingIDs:
            if (self.fo.getUniverse().getBuilding(ixBuilding).buildingTypeName == sBuilding):
                return True

        return False


    def fGetMaxPopulation(self, oFoPlanet, sSpecies, bPrintCalculation = False):
        """
        Return None in case the planet is uninhabitable.
        """

        TARGET_POPULATION_BEFORE_SCALING_PRIORITY = 10
        TARGET_POPULATION_AFTER_SCALING_PRIORITY  = 14

        HabitableSizeModifier = {
            TARGET_POPULATION_BEFORE_SCALING_PRIORITY: {
                'GRO_CYBORG': {
                    self.fo.planetEnvironment.hostile: 2
                },
                'GRO_SYMBIOTIC_BIO': {
                    self.fo.planetEnvironment.poor:     1,
                    self.fo.planetEnvironment.adequate: 1,
                    self.fo.planetEnvironment.good:     1
                },
                'GRO_XENO_GENETICS': {
                    self.fo.planetEnvironment.hostile:  1,
                    self.fo.planetEnvironment.poor:     2,
                    self.fo.planetEnvironment.adequate: 2
                },
                'GRO_XENO_HYBRIDS': {
                    self.fo.planetEnvironment.hostile: 2,
                    self.fo.planetEnvironment.poor:    1
                }
            },
            TARGET_POPULATION_AFTER_SCALING_PRIORITY: {
                'CON_NDIM_STRC': {
                    self.fo.planetEnvironment.uninhabitable: 2,
                    self.fo.planetEnvironment.hostile:       2,
                    self.fo.planetEnvironment.poor:          2,
                    self.fo.planetEnvironment.adequate:      2,
                    self.fo.planetEnvironment.good:          2
                },
                'CON_ORBITAL_HAB': {
                    self.fo.planetEnvironment.uninhabitable: 1,
                    self.fo.planetEnvironment.hostile:       1,
                    self.fo.planetEnvironment.poor:          1,
                    self.fo.planetEnvironment.adequate:      1,
                    self.fo.planetEnvironment.good:          1
                },
                'GRO_SUBTER_HAB': {
                    self.fo.planetEnvironment.uninhabitable: 1,
                    self.fo.planetEnvironment.hostile:       1,
                    self.fo.planetEnvironment.poor:          1,
                    self.fo.planetEnvironment.adequate:      1,
                    self.fo.planetEnvironment.good:          1
                }
            }
        }


        def iGetHabitableSizeModifier(iPriority, bPrintCalculation = False):
            iModifier = 0

            for iDictPriority, TechnologyDict in HabitableSizeModifier.items():
                if (iDictPriority == iPriority):
                    for sTechnology, iPlanetEnvironmentDict in TechnologyDict.items():
                        if (sTechnology in sAvailableTechFrozenset):
                            if (oFoPlanet.type in iPlanetEnvironmentDict):
                                iModifier += iPlanetEnvironmentDict[oFoPlanet.type]

                                if (bPrintCalculation):
                                    print 'priority %d, technology \'%s\', planet environment %d, modifier %d' % (
                                        iPriority,
                                        sTechnology,
                                        oFoPlanet.type,
                                        iPlanetEnvironmentDict[oFoPlanet.type]
                                    )

            return iModifier


        oFoSpecies = self.fo.getSpecies(sSpecies)
        oFoPlanetEnvironment = oFoSpecies.getPlanetEnvironment(oFoPlanet.type)

        if (bPrintCalculation):
            print 'Planet %d population calculation for \'%s\':' % (oFoPlanet.id, sSpecies)

        if (oFoPlanetEnvironment == self.fo.planetEnvironment.uninhabitable):
            if (bPrintCalculation):
                print 'Planet is uninhabitable for species.'

            return None

        if (self.bPlanetHasBuilding(oFoPlanet, 'BLD_GATEWAY_VOID')):
            if (bPrintCalculation):
                print 'Planet is uninhabitable due to \'BLD_GATEWAY_VOID\'.'

            return None

        fHabitableSize = oFoPlanet.habitableSize
        fMaximumPopulation = fHabitableSize

        if (bPrintCalculation):
            print 'habitable size %.2f' % (fHabitableSize)

        sAvailableTechFrozenset = self.fo.getEmpire().availableTechs

        fMaximumPopulation += iGetHabitableSizeModifier(TARGET_POPULATION_BEFORE_SCALING_PRIORITY, bPrintCalculation) * fHabitableSize
        fMaximumPopulation += iGetHabitableSizeModifier(TARGET_POPULATION_AFTER_SCALING_PRIORITY, bPrintCalculation) * fHabitableSize

        if (
            ('GRO_PLANET_ECOL' in sAvailableTechFrozenset) and
            (not 'GRO_SYMBIOTIC_BIO' in sAvailableTechFrozenset)
        ):
            if (oFoPlanetEnvironment in [self.fo.planetEnvironment.adequate, self.fo.planetEnvironment.good]):
                fMaximumPopulation += 1

                if (bPrintCalculation):
                    print '\'GRO_PLANET_ECOL\': +1'

        return fMaximumPopulation


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

                    self.fGetMaxPopulation(oFoPlanet, oFoPlanet.speciesName, True)
