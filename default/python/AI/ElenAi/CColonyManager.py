"""
This is the colony and outpost manager.
"""

from __future__ import print_function

from ElenAi.CManager import CManager
from ElenAi.CProductionQueue import CProductionQueue


class CColonyManager(CManager):


    def __init__(self, fo):
        super(CColonyManager, self).__init__(fo)

        # print(frozenset(self.__tsGetSpecies()))


    def vManage(self):
        for ixSystem in self.tixGetOwnSystem():
            self.vManageSystem(ixSystem)


    def tixGetOwnSystem(self):
        oFoUniverse = self.fo.getUniverse()

        for ixSystem in oFoUniverse.systemIDs:
            oFoSystem = oFoUniverse.getSystem(ixSystem)

            for ixPlanet in oFoSystem.planetIDs:
                oFoPlanet = oFoUniverse.getPlanet(ixPlanet)

                if (self._bIsOwn(oFoPlanet)):
                    yield ixSystem
                    break


    def vConditionallyAddBuilding(self, ixPlanet, sBuilding):
        oFoUniverse = self.fo.getUniverse()
        oProductionQueue = CProductionQueue(self.fo)

        if (not self.fo.getEmpire().canBuild(self.fo.buildType.building, sBuilding, ixPlanet)):
            return

        if (not oProductionQueue.bIsEnqueuedBuilding(ixPlanet, sBuilding)):
            oProductionQueue.vEnqueueBuilding(ixPlanet, sBuilding)


    def vManageSystem(self, ixSystem):
        oFoUniverse = self.fo.getUniverse()
        oFoSystem = oFoUniverse.getSystem(ixSystem)
        oProductionQueue = CProductionQueue(self.fo)

        for ixPlanet in oFoSystem.planetIDs:
            oFoPlanet = oFoUniverse.getPlanet(ixPlanet)

            if (self._bIsOwn(oFoPlanet)):
                for ixBuilding in oFoPlanet.buildingIDs:
                    oFoBuilding = oFoUniverse.getBuilding(ixBuilding)

                    # @todo If the whole empire has no BLD_IMPERIAL_PALACE, build a new one!

                    if (oFoBuilding.buildingTypeName == 'BLD_IMPERIAL_PALACE'):
                        self.vConditionallyAddBuilding(ixPlanet, 'BLD_MEGALITH')
                        self.vConditionallyAddBuilding(ixPlanet, 'BLD_STOCKPILING_CENTER')

                        # @todo Also build the following buildings redundantly.

                        self.vConditionallyAddBuilding(ixPlanet, 'BLD_GENOME_BANK')
                        self.vConditionallyAddBuilding(ixPlanet, 'BLD_INDUSTRY_CENTER')
                        self.vConditionallyAddBuilding(ixPlanet, 'BLD_NEUTRONIUM_SYNTH')

                    if (oFoBuilding.buildingTypeName == 'BLD_CULTURE_ARCHIVES'):
                        self.vConditionallyAddBuilding(ixPlanet, 'BLD_AUTO_HISTORY_ANALYSER')

            for sSpecial in oFoPlanet.specials:
                if (sSpecial in frozenset(['EXTINCT_BANFORO_SPECIAL', 'EXTINCT_KILANDOW_SPECIAL', 'EXTINCT_MISIORLA_SPECIAL'])):
                    self.vConditionallyAddBuilding(ixPlanet, 'BLD_XENORESURRECTION_LAB')
                else:
                    print('Unsupported special \'%s\' for planet %d!' % (sSpecial, ixPlanet))


    def __tsGetSpecies(self):
        """
        Return each species the empire has access to.
        """

        oFoUniverse = self.fo.getUniverse()

        for ixPlanet in oFoUniverse.planetIDs:
            oFoPlanet = oFoUniverse.getPlanet(ixPlanet)

            if (self._bIsOwn(oFoPlanet)):
                yield oFoPlanet.speciesName

        SpeciesDict = {
            'SP_EXOBOT': 'PRO_EXOBOTS',
            'SP_BANFORO': 'TECH_COL_BANFORO',
            'SP_KILANDOW': 'TECH_COL_KILANDOW',
            'SP_MISIORLA': 'TECH_COL_MISIORLA'
        }

        # @todo Is it enough to own the technology or is also a corresponding 'BLD_XENORESURRECTION_LAB' required?

        for sSpecies, sTechnology in SpeciesDict.items():
            if (self.fo.getEmpire().getTechStatus(sTechnology) == self.fo.techStatus.complete):
                yield sSpecies
