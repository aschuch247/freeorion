"""
This is the colony and outpost manager.
"""

from __future__ import print_function

from ElenAi.CManager import CManager
from ElenAi.CProductionQueue import CProductionQueue


class CColonyManager(CManager):


    def __init__(self, fo, oUniverse, oEmpireManager, oEmpireRelation, oSpeciesData):
        super(CColonyManager, self).__init__(fo)

        self.__m_oUniverse = oUniverse
        self.__m_oEmpireManager = oEmpireManager
        self.__m_oEmpireRelation = oEmpireRelation
        self.__m_oSpeciesData = oSpeciesData


    def vManage(self):
        for oSystem in self.__m_oUniverse.toGetSystem():
            self.vManageSystem(oSystem)


    def vConditionallyAddBuilding(self, oPlanet, sBuilding):
        ixPlanet = oPlanet.ixGetPlanet()
        oProductionQueue = CProductionQueue(self.fo)

        if (not self.fo.getEmpire().canBuild(self.fo.buildType.building, sBuilding, ixPlanet)):
            return

        if (not oProductionQueue.bIsEnqueuedBuilding(ixPlanet, sBuilding)):
            oProductionQueue.vEnqueueBuilding(ixPlanet, sBuilding)


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

                for sSpecial in frozenset(['EXTINCT_BANFORO_SPECIAL', 'EXTINCT_KILANDOW_SPECIAL', 'EXTINCT_MISIORLA_SPECIAL']):
                    if (oPlanet.bHasSpecial(sSpecial)):
                        self.vConditionallyAddBuilding(oPlanet, 'BLD_XENORESURRECTION_LAB')

                    # @todo print('Unsupported special \'%s\' for planet %d!' % (sSpecial, oPlanet.ixGetPlanet()))
