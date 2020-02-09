"""
This is the fleet movement manager.
"""

from __future__ import print_function

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

        for ixShip in self.tixGetMovingShip(self.tixGetOwnScoutShip()):
            oFoShip = oFoUniverse.getShip(ixShip)

            # If a scout moving to a system, the system is either already explored, or about to be explored.

            setSystemUnexploredTargeted.add(oFoUniverse.getFleet(oFoShip.fleetID).finalDestinationID)

        ixEnemyFleetSystemSet = set(self.tixGetEnemyFleetSystem())

        for ixShip in self.tixGetIdleShip(self.tixGetOwnScoutShip()):
            oFoShip = oFoUniverse.getShip(ixShip)

            # The scout ship is supposed to be located in a system, not moving.

            oGraphRouter = self.m_oUniverse.oGetGraphRouter(oFoShip.systemID, CGraphAdvisor(ixEnemyFleetSystemSet))

            # Only consider unexplored systems which are not yet targeted by scouts.

            # @todo However, it might be possible that another idle scout is closer to the unexplored system. Try to
            # find the closest idle scout first (search by system), and then give orders.

            ixSystemClosestUnexplored = oGraphRouter.ixGetClosestGraphNode(setSystemUnexplored.difference(setSystemUnexploredTargeted))

            if (ixSystemClosestUnexplored is not None):

                # In case the fleet is made up of multiple ships, split the ship from the fleet.

                if (not self.bIsSingleShipInFleet(ixShip)):
                    print(
                        'Splitting ship %d from fleet %d with result %d.' % (
                            ixShip,
                            oFoShip.fleetID,
                            self.fo.issueNewFleetOrder(oFoShip.design.name, ixShip)
                        )
                    )

                setSystemUnexploredTargeted.add(ixSystemClosestUnexplored)

                ixSystemList = oGraphRouter.tixGetPath(ixSystemClosestUnexplored)
                ixSystemCurrent = ixSystemList.pop(0) # remove system the fleet is in (current system)

                print(
                    'Ordering fleet %d to move to system %d with result %d (reset).' % (
                        oFoShip.fleetID,
                        ixSystemCurrent,
                        self.fo.issueFleetMoveOrder(oFoShip.fleetID, ixSystemCurrent)
                    )
                )

                for ixSystem in ixSystemList:
                    print(
                        'Ordering fleet %d to move to system %d with result %d (append).' % (
                            oFoShip.fleetID,
                            ixSystem,
                            self.fo.appendFleetMoveOrder(oFoShip.fleetID, ixSystem)
                        )
                    )


    def tixGetOwnShipWithPart(self, sPart):
        oFoUniverse = self.fo.getUniverse()

        for ixFleet in oFoUniverse.fleetIDs:
            oFoFleet = oFoUniverse.getFleet(ixFleet)

            if (self._bIsOwn(oFoFleet)):
                for ixShip in oFoFleet.shipIDs:
                    oFoShip = oFoUniverse.getShip(ixShip)
                    oFoShipDesign = oFoShip.design

                    for parts in oFoShipDesign.parts:
                        if (parts == sPart):
                            yield ixShip
                            break # next ship


    def tixGetOwnScoutShip(self):
        for ixShip in self.tixGetOwnShipWithPart('DT_DETECTOR_1'):
            yield ixShip


    def tixGetIdleShip(self, tixShip):
        oFoUniverse = self.fo.getUniverse()

        for ixShip in tixShip:
            oFoFleet = oFoUniverse.getFleet(oFoUniverse.getShip(ixShip).fleetID)

            if (oFoFleet.finalDestinationID == -1):
                yield ixShip


    def tixGetMovingShip(self, tixShip):
        oFoUniverse = self.fo.getUniverse()

        for ixShip in tixShip:
            oFoFleet = oFoUniverse.getFleet(oFoUniverse.getShip(ixShip).fleetID)

            if (oFoFleet.finalDestinationID != -1):
                yield ixShip


    def tixGetEnemyFleetSystem(self):
        oFoUniverse = self.fo.getUniverse()

        for ixFleet in oFoUniverse.fleetIDs:
            oFoFleet = oFoUniverse.getFleet(ixFleet)

            if (not self._bIsOwn(oFoFleet)):
                if (oFoFleet.systemID != -1):

                    # The fleet is stationary.

                    yield oFoFleet.systemID
                elif (oFoFleet.finalDestinationID != -1):

                    # The fleet is moving.

                    yield oFoFleet.finalDestinationID


    def bIsSingleShipInFleet(self, ixShip):
        oFoUniverse = self.fo.getUniverse()

        return oFoUniverse.getFleet(oFoUniverse.getShip(ixShip).fleetID).numShips == 1
