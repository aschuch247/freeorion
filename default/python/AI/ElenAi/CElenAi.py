"""
This is ElenAI, an AI module.
"""

from ElenAi.Adapter.CFleetAdapter import CFleetAdapter
from ElenAi.Adapter.CPlanetAdapter import CPlanetAdapter
from ElenAi.Adapter.CShipAdapter import CShipAdapter
from ElenAi.Adapter.CSystemAdapter import CSystemAdapter
from ElenAi.CColonisationManager import CColonisationManager
from ElenAi.CColonyManager import CColonyManager
from ElenAi.CColonyPredictor import CColonyPredictor
from ElenAi.CEmpireManager import CEmpireManager
from ElenAi.CEmpireRelation import CEmpireRelation
from ElenAi.CFleetHandler import CFleetHandler
from ElenAi.CFleetMovementManager import CFleetMovementManager
from ElenAi.CFleetProductionManager import CFleetProductionManager
from ElenAi.CProductionQueue import CProductionQueue
from ElenAi.CResearchManager import CResearchManager
from ElenAi.CResearchQueue import CResearchQueue
from ElenAi.CSpeciesDataDynamic import CSpeciesDataDynamic
from ElenAi.CUniverse import CUniverse


class CElenAi(object):


    def vGenerateOrders(self, fo):
        oUniverse = self.oGetUniverse(fo)
        oFleetHandler = self.oGetFleetHandler(fo)

        # @todo Show turn number and site report.

        oEmpireRelation = CEmpireRelation(fo.empireID())
        oEmpireManager = CEmpireManager(oUniverse, oEmpireRelation, fo.getEmpire().availableTechs)

        oProductionQueue = CProductionQueue(fo)
        oResearchQueue = CResearchQueue(fo)

        oColonyPredictor = CColonyPredictor(fo.getEmpire().availableTechs)

        oColonisationManager = CColonisationManager(fo, oUniverse, oEmpireManager, oEmpireRelation, oColonyPredictor, CSpeciesDataDynamic(fo))
        oColonisationManager.vManage()

        oColonyManager = CColonyManager(fo, oUniverse, oEmpireManager, oEmpireRelation, oColonisationManager, oProductionQueue, CSpeciesDataDynamic(fo))
        oColonyManager.vManage()

        oFleetMovementManager = CFleetMovementManager(fo, oUniverse, oEmpireRelation, oFleetHandler, oColonisationManager)
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
            oSystem = CSystemAdapter(oFoSystem).oGetSystem()

            oUniverse.vAddSystem(oSystem)

            for ixPlanet in oFoSystem.planetIDs:
                oFoPlanet = oFoUniverse.getPlanet(ixPlanet)
                oPlanet = CPlanetAdapter(oFoUniverse, oFoPlanet).oGetPlanet()

                oSystem.vAddPlanet(oPlanet)

        for ixSystem in oFoUniverse.systemIDs:
            for ixSystemNeighbour in oFoUniverse.getImmediateNeighbors(ixSystem, fo.empireID()):
                oUniverse.vLinkSystem(ixSystem, ixSystemNeighbour)

        # oUniverse.vDump()

        return oUniverse


    def oGetFleetHandler(self, fo):
        oFleetHandler = CFleetHandler()
        oFoUniverse = fo.getUniverse()

        for ixFleet in oFoUniverse.fleetIDs:
            oFoFleet = oFoUniverse.getFleet(ixFleet)
            oFleet = CFleetAdapter(oFoFleet).oGetFleet()

            oFleetHandler.vAddFleet(oFleet)

            for ixShip in oFoFleet.shipIDs:
                oFoShip = oFoUniverse.getShip(ixShip)
                oShip = CShipAdapter(oFoShip).oGetShip()

                oFleet.vAddShip(oShip)

        oFleetHandler.vDump()

        return oFleetHandler
