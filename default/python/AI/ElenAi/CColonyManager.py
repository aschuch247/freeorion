"""
This is the colony and outpost manager.
"""

from ElenAi.CManager import CManager
from ElenAi.CProductionQueue import CProductionQueue


class CColonyManager(CManager):


    def __init__(self, fo):
        super(CColonyManager, self).__init__(fo)


    def vManage(self):
        for ixSystem in self.tixGetOwnSystem():
            self.vManageSystem(ixSystem)


    def bIsOwn(self, oUniverseObject):
        return oUniverseObject.ownedBy(self.fo.empireID())


    def tixGetOwnSystem(self):
        oFoUniverse = self.fo.getUniverse()

        for ixSystem in oFoUniverse.systemIDs:
            oFoSystem = oFoUniverse.getSystem(ixSystem)

            for ixPlanet in oFoSystem.planetIDs:
                oFoPlanet = oFoUniverse.getPlanet(ixPlanet)

                if (self.bIsOwn(oFoPlanet)):
                    yield ixSystem
                    break


    def vConditionallyAddBuilding(self, ixPlanet, sBuilding):
        oFoUniverse = self.fo.getUniverse()
        oProductionQueue = CProductionQueue(self.fo)

        if (not self.fo.getEmpire().buildingTypeAvailable(sBuilding)):
            return

        bHasBuilding = False

        for ixBuilding in oFoUniverse.getPlanet(ixPlanet).buildingIDs:
            oFoBuilding = oFoUniverse.getBuilding(ixBuilding)

            if (oFoBuilding.buildingTypeName == sBuilding):
                bHasBuilding = True
                break

        if (not bHasBuilding):
            if (not oProductionQueue.bIsEnqueuedBuilding(ixPlanet, sBuilding)):
                oProductionQueue.vEnqueueBuilding(ixPlanet, sBuilding)


    def vManageSystem(self, ixSystem):
        oFoUniverse = self.fo.getUniverse()
        oFoSystem = oFoUniverse.getSystem(ixSystem)
        oProductionQueue = CProductionQueue(self.fo)

        for ixPlanet in oFoSystem.planetIDs:
            oFoPlanet = oFoUniverse.getPlanet(ixPlanet)

            if (self.bIsOwn(oFoPlanet)):
                for ixBuilding in oFoPlanet.buildingIDs:
                    oFoBuilding = oFoUniverse.getBuilding(ixBuilding)

                    # @todo If the whole empire has no BLD_IMPERIAL_PALACE, build a new one!

                    if (oFoBuilding.buildingTypeName == 'BLD_IMPERIAL_PALACE'):
                        self.vConditionallyAddBuilding(ixPlanet, 'BLD_MEGALITH')

                        # @todo Also build BLD_GENOME_BANK redundantly.

                        self.vConditionallyAddBuilding(ixPlanet, 'BLD_GENOME_BANK')

                    if (oFoBuilding.buildingTypeName == 'BLD_CULTURE_ARCHIVES'):
                        self.vConditionallyAddBuilding(ixPlanet, 'BLD_AUTO_HISTORY_ANALYSER')
