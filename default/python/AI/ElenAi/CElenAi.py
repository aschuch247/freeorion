"""
This is ElenAI, an AI module.
"""

from ElenAi.CColonisationManager import CColonisationManager
from ElenAi.CColonyManager import CColonyManager
from ElenAi.CFleetMovementManager import CFleetMovementManager
from ElenAi.CFleetProductionManager import CFleetProductionManager
from ElenAi.CPlanetConverter import CPlanetConverter
from ElenAi.CProductionQueue import CProductionQueue
from ElenAi.CResearchManager import CResearchManager
from ElenAi.CResearchQueue import CResearchQueue
from ElenAi.CSystemConverter import CSystemConverter
from ElenAi.CUniverse import CUniverse


class CElenAi(object):


    def vGenerateOrders(self, fo):
        oUniverse = self.oGetUniverse(fo)

        # @todo Show turn number and site report.

        oProductionQueue = CProductionQueue(fo)
        oResearchQueue = CResearchQueue(fo)

        oColonisationManager = CColonisationManager(fo)
        oColonisationManager.vManage()

        oColonyManager = CColonyManager(fo)
        oColonyManager.vManage()

        oFleetMovementManager = CFleetMovementManager(fo, oUniverse)
        oFleetMovementManager.vManage()

        oFleetProductionManager = CFleetProductionManager(fo, oProductionQueue)
        oFleetProductionManager.vManage()

        oResearchManager = CResearchManager(fo, oResearchQueue)
        oResearchManager.vManage()

        oProductionQueue.vLog()
        oResearchQueue.vLog()


    def oGetUniverse(self, fo):
        oUniverse = CUniverse()
        oFoUniverse = fo.getUniverse()

        for ixSystem in oFoUniverse.systemIDs:
            oFoSystem = oFoUniverse.getSystem(ixSystem)
            oSystem = CSystemConverter(oFoSystem).oGetSystem()

            oUniverse.vAddSystem(oSystem)

            for ixPlanet in oFoSystem.planetIDs:
                oFoPlanet = oFoUniverse.getPlanet(ixPlanet)
                oPlanet = CPlanetConverter(oFoPlanet).oGetPlanet()

                oSystem.vAddPlanet(oPlanet)

        for ixSystem in oFoUniverse.systemIDs:
            for ixSystemNeighbour in oFoUniverse.getImmediateNeighbors(ixSystem, fo.empireID()):
                oUniverse.vLinkSystem(ixSystem, ixSystemNeighbour)

        return oUniverse
