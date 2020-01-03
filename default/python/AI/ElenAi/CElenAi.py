"""
This is ElenAI, an AI module.
"""

from ElenAi.CColonyManager import CColonyManager
from ElenAi.CFleetMovementManager import CFleetMovementManager
from ElenAi.CResearchManager import CResearchManager
from ElenAi.CResearchQueue import CResearchQueue
from ElenAi.CProductionQueue import CProductionQueue
from ElenAi.CSystem import CSystem
from ElenAi.CUniverse import CUniverse
from ElenAi.CUniverseAssessment import CUniverseAssessment


class CElenAi(object):


    def vGenerateOrders(self, fo):
        oUniverseAssessment = CUniverseAssessment(fo)
        oUniverseAssessment.vAssessUniverse()

        oUniverse = self.oGetUniverse(fo)

        oColonyManager = CColonyManager(fo)
        oColonyManager.vManage()

        oFleetMovementManager = CFleetMovementManager(fo, oUniverse)
        oFleetMovementManager.vManage()

        oResearchManager = CResearchManager(fo)
        oResearchManager.vManage()

        oProductionQueue = CProductionQueue(fo)
        oProductionQueue.vLog()

        oResearchQueue = CResearchQueue(fo)
        oResearchQueue.vLog()


    def oGetUniverse(self, fo):
        oUniverse = CUniverse()
        oFoUniverse = fo.getUniverse()

        for ixSystem in oFoUniverse.systemIDs:
            oFoSystem = oFoUniverse.getSystem(ixSystem)

            oUniverse.vAddSystem(ixSystem, CSystem(oFoSystem.x, oFoSystem.y))

        for ixSystem in oFoUniverse.systemIDs:
            for ixSystemNeighbour in oFoUniverse.getImmediateNeighbors(ixSystem, fo.empireID()):
                oUniverse.vLinkSystem(ixSystem, ixSystemNeighbour)

        return oUniverse
