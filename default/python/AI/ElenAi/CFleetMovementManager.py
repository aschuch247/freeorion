"""
This is the fleet movement manager.
"""

from ElenAi.CGraphAdvisor import CGraphAdvisor
from ElenAi.CManager import CManager


class CFleetMovementManager(CManager):


    def __init__(self, fo, oUniverse):
        super(CFleetMovementManager, self).__init__(fo)

        self.m_oUniverse = oUniverse


    def vManage(self):
        oFoUniverse = self.fo.getUniverse()
        oFoEmpire = self.fo.getEmpire()

        # Get a list of known systems that have not been explored yet.

        setSystemUnexplored = set(oFoUniverse.systemIDs).difference(oFoEmpire.exploredSystemIDs)
        setSystemUnexploredTargeted = set()

        for ixShip in self.tixGetMovingScoutShip():
            oFoShip = oFoUniverse.getShip(ixShip)

            # If a scout moving to a system, the system is either already explored, or about to be explored.

            setSystemUnexploredTargeted.add(oFoUniverse.getFleet(oFoShip.fleetID).finalDestinationID)

        ixEnemyFleetSystemSet = set(self.tixGetEnemyFleetSystem())

        for ixShip in self.tixGetIdleScoutShip():
            oFoShip = oFoUniverse.getShip(ixShip)

            # The scout ship is supposed to be located in a system, not moving.

            oGraphRouter = self.m_oUniverse.oGetGraphRouter(oFoShip.systemID, CGraphAdvisor(ixEnemyFleetSystemSet))

            # Only consider unexplored systems which are not yet targeted by scouts.

            ixSystemClosestUnexplored = oGraphRouter.ixGetClosestGraphNode(setSystemUnexplored.difference(setSystemUnexploredTargeted))

            if (ixSystemClosestUnexplored is not None):
                setSystemUnexploredTargeted.add(ixSystemClosestUnexplored)

                self.fo.issueNewFleetOrder(oFoShip.design.name, ixShip)
                self.fo.issueFleetMoveOrder(oFoShip.fleetID, ixSystemClosestUnexplored)


    def bIsOwn(self, oUniverseObject):
        return oUniverseObject.ownedBy(self.fo.empireID())


    def tixGetIdleScoutShip(self):
        oFoUniverse = self.fo.getUniverse()

        for ixFleet in oFoUniverse.fleetIDs:
            oFoFleet = oFoUniverse.getFleet(ixFleet)

            if (self.bIsOwn(oFoFleet)):
                if (oFoFleet.finalDestinationID == -1):
                    for ixShip in oFoFleet.shipIDs:
                        oFoShip = oFoUniverse.getShip(ixShip)
                        oFoShipDesign = oFoShip.design

                        for parts in oFoShipDesign.parts:
                            if (parts == 'DT_DETECTOR_1'):
                                yield ixShip
                                break # next ship

    def tixGetMovingScoutShip(self):
        oFoUniverse = self.fo.getUniverse()

        for ixFleet in oFoUniverse.fleetIDs:
            oFoFleet = oFoUniverse.getFleet(ixFleet)

            if (self.bIsOwn(oFoFleet)):
                if (oFoFleet.finalDestinationID != -1):
                    for ixShip in oFoFleet.shipIDs:
                        oFoShip = oFoUniverse.getShip(ixShip)
                        oFoShipDesign = oFoShip.design

                        for parts in oFoShipDesign.parts:
                            if (parts == 'DT_DETECTOR_1'):
                                yield ixShip
                                break # next ship

    def tixGetEnemyFleetSystem(self):
        oFoUniverse = self.fo.getUniverse()

        for ixFleet in oFoUniverse.fleetIDs:
            oFoFleet = oFoUniverse.getFleet(ixFleet)

            if (not self.bIsOwn(oFoFleet)):
                if (oFoFleet.systemID != -1):

                    # The fleet is stationary.

                    yield oFoFleet.systemID
                elif (oFoFleet.finalDestinationID != -1):

                    # The fleet is moving.

                    yield oFoFleet.finalDestinationID
