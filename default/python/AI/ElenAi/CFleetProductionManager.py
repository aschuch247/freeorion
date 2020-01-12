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

        ixScoutShipDesign = self.ixGetScoutShipDesign()
        ixOutpostShipDesign = self.ixGetOutpostShipDesign()

        for ixBuilding in oFoUniverse.buildingIDs:
            oFoBuilding = oFoUniverse.getBuilding(ixBuilding)

            if (oFoBuilding.ownedBy(self.fo.empireID())):
                if (oFoBuilding.buildingTypeName == 'BLD_SHIPYARD_BASE'):
                    self.vBuildShip(oFoBuilding.planetID, ixScoutShipDesign)
                    self.vBuildShip(oFoBuilding.planetID, ixOutpostShipDesign)


    def ixGetShipDesignWithPart(self, sPart):
        oFoEmpire = self.fo.getEmpire()

        for ixShipDesign in oFoEmpire.availableShipDesigns:
            oFoShipDesign = self.fo.getShipDesign(ixShipDesign)

            if (oFoShipDesign.speed > 0.0):
                for parts in oFoShipDesign.parts:
                    if (parts == sPart):
                        return ixShipDesign

        return -1


    def ixGetScoutShipDesign(self):
        return self.ixGetShipDesignWithPart('DT_DETECTOR_1')


    def ixGetOutpostShipDesign(self):
        return self.ixGetShipDesignWithPart('CO_OUTPOST_POD')


    def vBuildShip(self, ixPlanet, ixShipDesign):
        if (ixShipDesign == -1):
            print 'Cancelled building invalid ship design on planet %d.' % (ixPlanet)
            return

        if (not self.m_oProductionQueue.bIsEnqueuedShipDesign(ixPlanet, ixShipDesign)):
            self.m_oProductionQueue.vEnqueueShipDesign(ixPlanet, ixShipDesign)
