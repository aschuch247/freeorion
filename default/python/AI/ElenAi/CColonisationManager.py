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

        bConsiderFullTerraforming = False

        # @todo Consider support for:
        # - BLD_HYPER_DAM
        # - DIM_RIFT_MASTER_SPECIAL
        # - HOMEWORLD_GROWTH_FOCUS_BOOST
        # - SP_LEMBALALAM
        # - TEMPORAL_ANOMALY_SPECIAL
        # - TIDAL_LOCK_SPECIAL
        # - XENOPHOBIC

        TARGET_POPULATION_BEFORE_SCALING_PRIORITY       = 10
        TARGET_POPULATION_SCALING_PRIORITY              = 12
        TARGET_POPULATION_AFTER_SCALING_PRIORITY        = 14
        TARGET_POPULATION_LAST_BEFORE_OVERRIDE_PRIORITY = 16
        TARGET_POPULATION_OVERRIDE_PRIORITY             = 17

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


        def fAddPopulationBonus(sName, fPopulationBonus, bPrintCalculation = False):
            if (bPrintCalculation):
                print('%s: %+.2f' % (sName, fPopulationBonus))

            return fPopulationBonus


        def iGetHabitableSizeModifier(iPriority, bPrintCalculation = False):
            iModifier = 0

            for iDictPriority, TechnologyDict in HabitableSizeModifier.items():
                if (iDictPriority == iPriority):
                    for sTechnology, iPlanetEnvironmentDict in TechnologyDict.items():
                        if (sTechnology in sAvailableTechFrozenset):
                            if (oFoPlanetEnvironment in iPlanetEnvironmentDict):
                                iModifier += iPlanetEnvironmentDict[oFoPlanetEnvironment]

                                if (bPrintCalculation):
                                    print(
                                        'priority %d, technology \'%s\', planet environment %d, modifier %+d' % (
                                            iPriority,
                                            sTechnology,
                                            oFoPlanetEnvironment,
                                            iPlanetEnvironmentDict[oFoPlanetEnvironment]
                                        )
                                    )

            return iModifier


        oFoSpecies = self.fo.getSpecies(sSpecies)
        oFoPlanetEnvironment = oFoSpecies.getPlanetEnvironment(oFoPlanet.type)

        if (bPrintCalculation):
            print('Planet %d population calculation for \'%s\':' % (oFoPlanet.id, sSpecies))

        # ENVIRONMENT_MODIFIER - TARGET_POPULATION_OVERRIDE_PRIORITY

        if (oFoPlanetEnvironment == self.fo.planetEnvironment.uninhabitable):
            if (bPrintCalculation):
                print('Planet is uninhabitable for species.')

            return None

        if (self.bPlanetHasBuilding(oFoPlanet, 'BLD_GATEWAY_VOID')):
            if (bPrintCalculation):
                print('Planet is uninhabitable due to \'BLD_GATEWAY_VOID\'.')

            return None

        fHabitableSize = oFoPlanet.habitableSize
        fMaximumPopulation = 0.0

        sAvailableTechFrozenset = self.fo.getEmpire().availableTechs
        sSpeciesTagFrozenset = frozenset(oFoSpecies.tags)
        sPlanetSpecialsFrozenset = frozenset(oFoPlanet.specials)

        fMaximumPopulation += iGetHabitableSizeModifier(TARGET_POPULATION_BEFORE_SCALING_PRIORITY, bPrintCalculation) * fHabitableSize

        # ENVIRONMENT_MODIFIER - TARGET_POPULATION_BEFORE_SCALING_PRIORITY

        EnvironmentalModifier = {
            self.fo.planetEnvironment.hostile: -4.0,
            self.fo.planetEnvironment.poor:    -2.0,
            self.fo.planetEnvironment.good:     3.0
        }

        fMaximumPopulation += fAddPopulationBonus('ENVIRONMENT_MODIFIER', EnvironmentalModifier.get(oFoPlanetEnvironment, 0) * fHabitableSize, bPrintCalculation)

        # BAD_POPULATION - TARGET_POPULATION_SCALING_PRIORITY

        if ('BAD_POPULATION' in sSpeciesTagFrozenset):
            fMaximumPopulation += fAddPopulationBonus('BAD_POPULATION', -0.25 * abs(fMaximumPopulation), bPrintCalculation)

        # GOOD_POPULATION - TARGET_POPULATION_SCALING_PRIORITY

        if ('GOOD_POPULATION' in sSpeciesTagFrozenset):
            fMaximumPopulation += fAddPopulationBonus('GOOD_POPULATION', 0.25 * abs(fMaximumPopulation), bPrintCalculation)

        # GASEOUS_BONUS - TARGET_POPULATION_SCALING_PRIORITY
        # @todo This calculation probably is wrong for a mix of GOOD_POPULATION and GASEOUS.

        if (('GASEOUS' in sSpeciesTagFrozenset) and (oFoPlanet.type == self.fo.planetType.gasGiant)):
            fMaximumPopulation += fAddPopulationBonus('GASEOUS_BONUS', -0.5 * abs(fMaximumPopulation), bPrintCalculation)

        fMaximumPopulation += iGetHabitableSizeModifier(TARGET_POPULATION_AFTER_SCALING_PRIORITY, bPrintCalculation) * fHabitableSize

        # GRO_PLANET_ECOL - TARGET_POPULATION_AFTER_SCALING_PRIORITY

        if (
            ('GRO_PLANET_ECOL' in sAvailableTechFrozenset) and
            (not 'GRO_SYMBIOTIC_BIO' in sAvailableTechFrozenset)
        ):
            if (oFoPlanetEnvironment in [self.fo.planetEnvironment.adequate, self.fo.planetEnvironment.good]):
                fMaximumPopulation += fAddPopulationBonus('GRO_PLANET_ECOL', 1.0, bPrintCalculation)

        # HOMEWORLD_BONUS_POPULATION - TARGET_POPULATION_AFTER_SCALING_PRIORITY

        if (oFoPlanet.id in oFoSpecies.homeworlds):
            fMaximumPopulation += fAddPopulationBonus('HOMEWORLD_BONUS_POPULATION', 2.0 * fHabitableSize, bPrintCalculation)

        # @todo HOMEWORLD_GROWTH_FOCUS_BOOST - TARGET_POPULATION_AFTER_SCALING_PRIORITY

        # SELF_SUSTAINING_BONUS - TARGET_POPULATION_AFTER_SCALING_PRIORITY

        if ('SELF_SUSTAINING' in sSpeciesTagFrozenset):
            fMaximumPopulation += fAddPopulationBonus('SELF_SUSTAINING_BONUS', 3.0 * fHabitableSize, bPrintCalculation)

        # GAIA_SPECIAL - TARGET_POPULATION_AFTER_SCALING_PRIORITY

        if ('GAIA_SPECIAL' in sPlanetSpecialsFrozenset):

            # SP_EXOBOT does not have any good planet environment.

            if ((bConsiderFullTerraforming and (sSpecies != 'SP_EXOBOT')) or (oFoPlanetEnvironment == self.fo.planetEnvironment.good)):
                fMaximumPopulation += fAddPopulationBonus('GAIA_SPECIAL', 3.0 * fHabitableSize, bPrintCalculation)

        # PHOTOTROPHIC_BONUS - TARGET_POPULATION_LAST_BEFORE_OVERRIDE_PRIORITY

        if ('PHOTOTROPHIC' in sSpeciesTagFrozenset):
            iStarType = self.fo.getUniverse().getSystem(oFoPlanet.systemID).starType

            if (fMaximumPopulation >= 0.0):
                PhototrophicModifier = {
                    self.fo.starType.blue:        3.0,
                    self.fo.starType.white:       1.5,
                    self.fo.starType.red:        -1.0,
                    self.fo.starType.neutron:    -1.0,
                    self.fo.starType.blackHole: -10.0,
                    self.fo.starType.noStar:    -10.0
                }

                fMaximumPopulation += fAddPopulationBonus('PHOTOTROPHIC_BONUS', PhototrophicModifier.get(iStarType, 0.0) * fHabitableSize, bPrintCalculation)

        return fMaximumPopulation


    def __bIsOwnColony(self, oFoPlanet):
        return self._bIsOwn(oFoPlanet) and (oFoPlanet.speciesName != '')

    def __bIsOwnOutpost(self, oFoPlanet):
        return self._bIsOwn(oFoPlanet) and (oFoPlanet.speciesName == '')

    def __vAssertTargetPopulation(self):
        oFoUniverse = self.fo.getUniverse()

        for ixPlanet in oFoUniverse.planetIDs:
            oFoPlanet = oFoUniverse.getPlanet(ixPlanet)

            if (self.__bIsOwnColony(oFoPlanet)):
                fActualMaxPopulation = oFoPlanet.initialMeterValue(self.fo.meterType.targetPopulation)
                fExpectedMaxPopulation = self.fGetMaxPopulation(oFoPlanet, oFoPlanet.speciesName)

                if (fActualMaxPopulation != fExpectedMaxPopulation):
                    print(
                        'Actual maximum population %.2f differs from expected maximum population %.2f for planet %d!' % (
                            fActualMaxPopulation,
                            fExpectedMaxPopulation,
                            ixPlanet
                        )
                    )

                    self.fGetMaxPopulation(oFoPlanet, oFoPlanet.speciesName, True)
            elif (self.__bIsOwnOutpost(oFoPlanet)):
                print('Planet %d is an outpost.' % (ixPlanet))
