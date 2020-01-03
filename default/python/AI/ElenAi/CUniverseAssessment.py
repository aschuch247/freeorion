"""
Assess the universe.
"""

from ElenAi.CSystem import CSystem
from ElenAi.CUniverse import CUniverse


class CUniverseAssessment(object):


    def __init__(self, fo):
        self.fo = fo


    def tixGetIdleScoutShip(self):
        oFoUniverse = self.fo.getUniverse()

        for ixFleet in oFoUniverse.fleetIDs:
            oFoFleet = oFoUniverse.getFleet(ixFleet)

            if oFoFleet.ownedBy(self.fo.empireID()):
                if (oFoFleet.finalDestinationID == -1) or (oFoFleet.finalDestinationID == oFoFleet.systemID):
                    for ixShip in oFoFleet.shipIDs:
                        oFoShip = oFoUniverse.getShip(ixShip)
                        oFoShipDesign = oFoShip.design

                        for parts in oFoShipDesign.parts:
                            if (parts == 'DT_DETECTOR_1'):
                                yield ixShip

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
            bScoutEnqueued = False

            for idx, oProductionQueueElement in enumerate(oFoEmpire.productionQueue):
                if (oProductionQueueElement.locationID == ixPlanet):
                    if (oProductionQueueElement.buildType == self.fo.buildType.ship):
                        if (oProductionQueueElement.designID == ixShipDesignScout):
                            bScoutEnqueued = True
                            break

            if (not bScoutEnqueued):
                print 'Enqueuing ship design %s at planet %s, system %s with result %d.' % (
                    self.fo.getShipDesign(ixShipDesignScout).name,
                    self.fo.getUniverse().getPlanet(ixPlanet).name,
                    self.fo.getUniverse().getSystem(self.fo.getUniverse().getPlanet(ixPlanet).systemID).name,
                    self.fo.issueEnqueueShipProductionOrder(ixShipDesignScout, ixPlanet)
                )


    def vAssessUniverse(self):
        oUniverse = CUniverse()
        oFoUniverse = self.fo.getUniverse()

        for ixSystem in oFoUniverse.systemIDs:
            oFoSystem = oFoUniverse.getSystem(ixSystem)
            # print 'I know system %s (%d).' % (oFoSystem.name, oFoSystem.systemID)

            if (oFoSystem.numWormholes != 0):
                print 'Wormholes found!'

            oUniverse.vAddSystem(ixSystem, CSystem(oFoSystem.x, oFoSystem.y))

        for ixSystem in oFoUniverse.systemIDs:
            for ixSystemNeighbour in oFoUniverse.getImmediateNeighbors(ixSystem, self.fo.empireID()):
                oUniverse.vLinkSystem(ixSystem, ixSystemNeighbour)

        oFoEmpire = self.fo.getEmpire()

        for ixSystem in oFoEmpire.exploredSystemIDs:
            oFoSystem = oFoUniverse.getSystem(ixSystem)
            # print 'I have explored system %s (%d).' % (oFoSystem.name, oFoSystem.systemID)

        # Get a list of known systems that have not been explored yet.

        setSystemUnexplored = set(oFoUniverse.systemIDs).difference(oFoEmpire.exploredSystemIDs)
        setSystemUnexploredTargeted = set()

        for ixShip in self.tixGetIdleScoutShip():
            oFoShip = oFoUniverse.getShip(ixShip)

            # The scout ship is supposed to be located in a system, not moving.

            oGraphRouter = oUniverse.oGetGraphRouter(oFoShip.systemID)

            # Only consider unexplored systems which are not yet targeted by scouts.

            ixSystemClosestUnexplored = oGraphRouter.ixGetClosestGraphNode(setSystemUnexplored.difference(setSystemUnexploredTargeted))

            setSystemUnexploredTargeted.add(ixSystemClosestUnexplored)

            self.fo.issueNewFleetOrder(oFoShip.design.name, ixShip)
            self.fo.issueFleetMoveOrder(oFoShip.fleetID, ixSystemClosestUnexplored)

        # Build scouts everywhere.

        for ixBuilding in oFoUniverse.buildingIDs:
            oFoBuilding = oFoUniverse.getBuilding(ixBuilding)

            if (oFoBuilding.ownedBy(self.fo.empireID())):
                if (oFoBuilding.buildingTypeName == 'BLD_SHIPYARD_BASE'):
                    self.vBuildScout(oFoBuilding.planetID)
