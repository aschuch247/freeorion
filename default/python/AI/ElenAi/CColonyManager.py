"""
This is the colony and outpost manager.
"""

from __future__ import print_function

from ElenAi.CColonyPredictor import CColonyPredictor
from ElenAi.CManager import CManager


class CColonyManager(CManager):


    def __init__(self, fo, oUniverse, oEmpireManager, oEmpireRelation, oColonisationManager, oProductionQueue, oSpeciesData):
        super(CColonyManager, self).__init__(fo)

        self.__m_oUniverse = oUniverse
        self.__m_oEmpireManager = oEmpireManager
        self.__m_oEmpireRelation = oEmpireRelation
        self.__m_oColonisationManager = oColonisationManager
        self.__m_oProductionQueue = oProductionQueue
        self.__m_oSpeciesData = oSpeciesData


    def vManage(self):
        for oSystem in self.__m_oUniverse.toGetSystem():
            self.vManageSystem(oSystem)


    def vConditionallyAddBuilding(self, oPlanet, sBuilding):
        ixPlanet = oPlanet.ixGetPlanet()

        if (not self.fo.getEmpire().canBuild(self.fo.buildType.building, sBuilding, ixPlanet)):
            return

        if (not self.__m_oProductionQueue.bIsEnqueuedBuilding(ixPlanet, sBuilding)):
            self.__m_oProductionQueue.vEnqueueBuilding(ixPlanet, sBuilding)


    def vManageSystem(self, oSystem):
        bIsOwnSystem = False

        for oPlanet in oSystem.toGetPlanet():
            if (self.__m_oEmpireRelation.bIsOwnPlanet(oPlanet)):
                bIsOwnSystem = True
                break

        if (not bIsOwnSystem):
            return

        for oPlanet in oSystem.toGetPlanet():
            if (self.__m_oEmpireRelation.bIsOwnPlanet(oPlanet)):
                if (oPlanet.bIsOutpost()):
                    dictColonisationOption = self.__m_oColonisationManager.dictGetColonisationOption()

                    ixSystem = oSystem.ixGetSystem()
                    ixPlanet = oPlanet.ixGetPlanet()

                    tupleColonisation = self.__m_oColonisationManager.tupleGetHighestPopulationColonisation(
                        ixSystem,
                        ixPlanet,
                        dictColonisationOption[ixSystem][ixPlanet]
                    )

                    self.vConditionallyAddBuilding(oPlanet, tupleColonisation[2].replace('SP_', 'BLD_COL_', 1))

                # @todo If the whole empire has no BLD_IMPERIAL_PALACE, build a new one!

                if (oPlanet.bHasBuilding('BLD_IMPERIAL_PALACE')):
                    self.vConditionallyAddBuilding(oPlanet, 'BLD_MEGALITH')
                    self.vConditionallyAddBuilding(oPlanet, 'BLD_STOCKPILING_CENTER')

                    # @todo Also build the following buildings redundantly.

                    self.vConditionallyAddBuilding(oPlanet, 'BLD_GENOME_BANK')
                    self.vConditionallyAddBuilding(oPlanet, 'BLD_INDUSTRY_CENTER')
                    self.vConditionallyAddBuilding(oPlanet, 'BLD_NEUTRONIUM_SYNTH')

                if (oPlanet.bHasBuilding('BLD_CULTURE_ARCHIVES')):
                    self.vConditionallyAddBuilding(oPlanet, 'BLD_AUTO_HISTORY_ANALYSER')

                if (oPlanet.bHasBuilding('BLD_SHIPYARD_BASE')):
                    self.vConditionallyAddBuilding(oPlanet, 'BLD_SHIPYARD_ORBITAL_DRYDOCK')
                    self.vConditionallyAddBuilding(oPlanet, 'BLD_SHIPYARD_ORG_ORB_INC')

                # BLD_ART_BLACK_HOLE
                # BLD_COLLECTIVE_NET
                # BLD_ENCLAVE_VOID
                # BLD_GAS_GIANT_GEN
                # BLD_LIGHTHOUSE
                # BLD_NEUTRONIUM_EXTRACTOR
                # BLD_SCANNING_FACILITY
                # BLD_SOL_ORB_GEN

                for sSpecial in frozenset(['EXTINCT_BANFORO_SPECIAL', 'EXTINCT_KILANDOW_SPECIAL', 'EXTINCT_MISIORLA_SPECIAL']):
                    if (oPlanet.bHasSpecial(sSpecial)):
                        self.vConditionallyAddBuilding(oPlanet, 'BLD_XENORESURRECTION_LAB')

                    # @todo print('Unsupported special \'%s\' for planet %d!' % (sSpecial, oPlanet.ixGetPlanet()))
