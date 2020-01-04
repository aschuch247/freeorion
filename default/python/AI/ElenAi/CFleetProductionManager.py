"""
This is the fleet production manager.
"""

from ElenAi.CManager import CManager


class CFleetProductionManager(CManager):


    def __init__(self, fo, oProductionQueue):
        super(CFleetProductionManager, self).__init__(fo)

        self.m_oProductionQueue = oProductionQueue


    def vManage(self):
        oFoUniverse = self.fo.getUniverse()
        oFoEmpire = self.fo.getEmpire()

        # Build scouts everywhere.

        for ixBuilding in oFoUniverse.buildingIDs:
            oFoBuilding = oFoUniverse.getBuilding(ixBuilding)

            if (oFoBuilding.ownedBy(self.fo.empireID())):
                if (oFoBuilding.buildingTypeName == 'BLD_SHIPYARD_BASE'):
                    self.vBuildScout(oFoBuilding.planetID)


    def vBuildScout(self, ixPlanet):
        oFoEmpire = self.fo.getEmpire()

        ixShipDesignScout = None

        for ixShipDesign in oFoEmpire.availableShipDesigns:
            oFoShipDesign = self.fo.getShipDesign(ixShipDesign)

            for parts in oFoShipDesign.parts:
                if (parts == 'DT_DETECTOR_1'):
                    ixShipDesignScout = ixShipDesign
                    break

        if (ixShipDesignScout is not None):
            if (not self.m_oProductionQueue.bIsEnqueuedShipDesign(ixPlanet, ixShipDesignScout)):
                self.m_oProductionQueue.vEnqueueShipDesign(ixPlanet, ixShipDesignScout)
