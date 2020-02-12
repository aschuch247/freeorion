"""
Predict the maximum colony population.
"""

from __future__ import print_function

from ElenAi.Constant.CPlanetEnvironment import CPlanetEnvironment
from ElenAi.Constant.CPlanetType import CPlanetType
from ElenAi.Constant.CStarType import CStarType


class CColonyPredictor(object):
    TARGET_POPULATION_BEFORE_SCALING_PRIORITY       = 10
    TARGET_POPULATION_SCALING_PRIORITY              = 12
    TARGET_POPULATION_AFTER_SCALING_PRIORITY        = 14
    TARGET_POPULATION_LAST_BEFORE_OVERRIDE_PRIORITY = 16
    TARGET_POPULATION_OVERRIDE_PRIORITY             = 17

    HabitableSizeModifier = {
        TARGET_POPULATION_BEFORE_SCALING_PRIORITY: {
            'GRO_CYBORG': {
                CPlanetEnvironment.hostile: 2
            },
            'GRO_SYMBIOTIC_BIO': {
                CPlanetEnvironment.poor:     1,
                CPlanetEnvironment.adequate: 1,
                CPlanetEnvironment.good:     1
            },
            'GRO_XENO_GENETICS': {
                CPlanetEnvironment.hostile:  1,
                CPlanetEnvironment.poor:     2,
                CPlanetEnvironment.adequate: 2
            },
            'GRO_XENO_HYBRIDS': {
                CPlanetEnvironment.hostile: 2,
                CPlanetEnvironment.poor:    1
            }
        },
        TARGET_POPULATION_AFTER_SCALING_PRIORITY: {
            'CON_NDIM_STRC': {
                CPlanetEnvironment.uninhabitable: 2,
                CPlanetEnvironment.hostile:       2,
                CPlanetEnvironment.poor:          2,
                CPlanetEnvironment.adequate:      2,
                CPlanetEnvironment.good:          2
            },
            'CON_ORBITAL_HAB': {
                CPlanetEnvironment.uninhabitable: 1,
                CPlanetEnvironment.hostile:       1,
                CPlanetEnvironment.poor:          1,
                CPlanetEnvironment.adequate:      1,
                CPlanetEnvironment.good:          1
            },
            'GRO_SUBTER_HAB': {
                CPlanetEnvironment.uninhabitable: 1,
                CPlanetEnvironment.hostile:       1,
                CPlanetEnvironment.poor:          1,
                CPlanetEnvironment.adequate:      1,
                CPlanetEnvironment.good:          1
            }
        }
    }


    def __init__(self, sTechnologyFrozenset):
        self.__m_sTechnologyFrozenset = sTechnologyFrozenset


    def __fAddPopulationBonus(self, sName, fPopulationBonus, bPrintCalculation = False):
        if (bPrintCalculation):
            print('%s: %+.2f' % (sName, fPopulationBonus))

        return fPopulationBonus


    def __iGetHabitableSizeModifier(self, iPriority, iPlanetEnvironment, bPrintCalculation = False):
        iModifier = 0

        for iDictPriority, TechnologyDict in self.HabitableSizeModifier.items():
            if (iDictPriority == iPriority):
                for sTechnology, iPlanetEnvironmentDict in TechnologyDict.items():
                    if (sTechnology in self.__m_sTechnologyFrozenset):
                        if (iPlanetEnvironment in iPlanetEnvironmentDict):
                            iModifier += iPlanetEnvironmentDict[iPlanetEnvironment]

                            if (bPrintCalculation):
                                print(
                                    'priority %d, technology \'%s\', planet environment %d, modifier %+d' % (
                                        iPriority,
                                        sTechnology,
                                        iPlanetEnvironment,
                                        iPlanetEnvironmentDict[iPlanetEnvironment]
                                    )
                                )

        return iModifier


    def fGetMaxPopulation(self, oPlanet, oSpecies, bPrintCalculation = False):
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

        if (bPrintCalculation):
            print('Planet %d population calculation for species \'%s\':' % (oPlanet.ixGetPlanet(), oSpecies.sGetName()))

        iPlanetEnvironment = oSpecies.iGetPlanetEnvironment(oPlanet.iGetPlanetType())

        # ENVIRONMENT_MODIFIER - TARGET_POPULATION_OVERRIDE_PRIORITY

        if (iPlanetEnvironment == CPlanetEnvironment.uninhabitable):
            if (bPrintCalculation):
                print('Planet is uninhabitable for species.')

            return None

        if (oPlanet.bHasBuilding('BLD_GATEWAY_VOID')):
            if (bPrintCalculation):
                print('Planet is uninhabitable due to \'BLD_GATEWAY_VOID\'.')

            return None

        iHabitableSize = oPlanet.iGetHabitableSize()
        fMaxPopulation = 0.0

        fMaxPopulation += self.__iGetHabitableSizeModifier(self.TARGET_POPULATION_BEFORE_SCALING_PRIORITY, iPlanetEnvironment, bPrintCalculation) * iHabitableSize

        # ENVIRONMENT_MODIFIER - TARGET_POPULATION_BEFORE_SCALING_PRIORITY

        EnvironmentalModifier = {
            CPlanetEnvironment.hostile: -4.0,
            CPlanetEnvironment.poor:    -2.0,
            CPlanetEnvironment.good:     3.0
        }

        fMaxPopulation += self.__fAddPopulationBonus('ENVIRONMENT_MODIFIER', EnvironmentalModifier.get(iPlanetEnvironment, 0) * iHabitableSize, bPrintCalculation)

        # BAD_POPULATION - TARGET_POPULATION_SCALING_PRIORITY

        if (oSpecies.bHasTag('BAD_POPULATION')):
            fMaxPopulation += self.__fAddPopulationBonus('BAD_POPULATION', -0.25 * abs(fMaxPopulation), bPrintCalculation)

        # GOOD_POPULATION - TARGET_POPULATION_SCALING_PRIORITY

        if (oSpecies.bHasTag('GOOD_POPULATION')):
            fMaxPopulation += self.__fAddPopulationBonus('GOOD_POPULATION', 0.25 * abs(fMaxPopulation), bPrintCalculation)

        # GASEOUS_BONUS - TARGET_POPULATION_SCALING_PRIORITY
        # @todo This calculation probably is wrong for a mix of GOOD_POPULATION and GASEOUS.

        if (oSpecies.bHasTag('GASEOUS') and (oPlanet.iGetPlanetType() == CPlanetType.gasGiant)):
            fMaxPopulation += self.__fAddPopulationBonus('GASEOUS_BONUS', -0.5 * abs(fMaxPopulation), bPrintCalculation)

        fMaxPopulation += self.__iGetHabitableSizeModifier(self.TARGET_POPULATION_AFTER_SCALING_PRIORITY, iPlanetEnvironment, bPrintCalculation) * iHabitableSize

        # GRO_PLANET_ECOL - TARGET_POPULATION_AFTER_SCALING_PRIORITY

        if (
            ('GRO_PLANET_ECOL' in self.__m_sTechnologyFrozenset) and
            (not 'GRO_SYMBIOTIC_BIO' in self.__m_sTechnologyFrozenset)
        ):
            if (iPlanetEnvironment in [CPlanetEnvironment.adequate, CPlanetEnvironment.good]):
                fMaxPopulation += self.__fAddPopulationBonus('GRO_PLANET_ECOL', 1.0, bPrintCalculation)

        # HOMEWORLD_BONUS_POPULATION - TARGET_POPULATION_AFTER_SCALING_PRIORITY

        if (oSpecies.bIsHomePlanet(oPlanet.ixGetPlanet())):
            fMaxPopulation += self.__fAddPopulationBonus('HOMEWORLD_BONUS_POPULATION', 2.0 * iHabitableSize, bPrintCalculation)

        # @todo HOMEWORLD_GROWTH_FOCUS_BOOST - TARGET_POPULATION_AFTER_SCALING_PRIORITY

        # SELF_SUSTAINING_BONUS - TARGET_POPULATION_AFTER_SCALING_PRIORITY

        if (oSpecies.bHasTag('SELF_SUSTAINING')):
            fMaxPopulation += self.__fAddPopulationBonus('SELF_SUSTAINING_BONUS', 3.0 * iHabitableSize, bPrintCalculation)

        # GAIA_SPECIAL - TARGET_POPULATION_AFTER_SCALING_PRIORITY

        if (oPlanet.bHasSpecial('GAIA_SPECIAL')):

            # SP_EXOBOT does not have any good planet environment.

            if ((bConsiderFullTerraforming and (sSpecies != 'SP_EXOBOT')) or (iPlanetEnvironment == CPlanetEnvironment.good)):
                fMaxPopulation += self.__fAddPopulationBonus('GAIA_SPECIAL', 3.0 * iHabitableSize, bPrintCalculation)

        # PHOTOTROPHIC_BONUS - TARGET_POPULATION_LAST_BEFORE_OVERRIDE_PRIORITY

        if (oSpecies.bHasTag('PHOTOTROPHIC')):
            iStarType = oPlanet.oGetSystem().iGetStarType()

            if (fMaxPopulation >= 0.0):
                PhototrophicModifier = {
                    CStarType.blue:        3.0,
                    CStarType.white:       1.5,
                    CStarType.red:        -1.0,
                    CStarType.neutron:    -1.0,
                    CStarType.blackHole: -10.0,
                    CStarType.noStar:    -10.0
                }

                fMaxPopulation += self.__fAddPopulationBonus('PHOTOTROPHIC_BONUS', PhototrophicModifier.get(iStarType, 0.0) * iHabitableSize, bPrintCalculation)

        return fMaxPopulation
