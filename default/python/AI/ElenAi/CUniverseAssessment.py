"""
Assess the universe.
"""

from ElenAi.CProductionQueue import CProductionQueue
from ElenAi.CSystem import CSystem
from ElenAi.CUniverse import CUniverse


class CUniverseAssessment(object):


    def __init__(self, fo):
        self.fo = fo


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
            oProductionQueue = CProductionQueue(self.fo)

            if (not oProductionQueue.bIsEnqueuedShipDesign(ixPlanet, ixShipDesignScout)):
                oProductionQueue.vEnqueueShipDesign(ixPlanet, ixShipDesignScout)


    def vAssessUniverse(self):
        oFoUniverse = self.fo.getUniverse()
        oFoEmpire = self.fo.getEmpire()

        # Build scouts everywhere.

        for ixBuilding in oFoUniverse.buildingIDs:
            oFoBuilding = oFoUniverse.getBuilding(ixBuilding)

            if (oFoBuilding.ownedBy(self.fo.empireID())):
                if (oFoBuilding.buildingTypeName == 'BLD_SHIPYARD_BASE'):
                    self.vBuildScout(oFoBuilding.planetID)
