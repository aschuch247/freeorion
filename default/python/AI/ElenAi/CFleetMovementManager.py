"""
This is the fleet movement manager.
"""

from __future__ import print_function

from ElenAi.CGraphAdvisor import CGraphAdvisor
from ElenAi.CManager import CManager


class CFleetMovementManager(CManager):


    def __init__(self, fo, oUniverse, oEmpireRelation, oFleetHandler, oColonisationManager):
        super(CFleetMovementManager, self).__init__(fo)

        self.__m_oUniverse = oUniverse
        self.__m_oEmpireRelation = oEmpireRelation
        self.__m_oFleetHandler = oFleetHandler
        self.__m_oColonisationManager = oColonisationManager


    def vManage(self):
        oFoUniverse = self.fo.getUniverse()
        oFoEmpire = self.fo.getEmpire()

        ixEnemyFleetSystemFrozenset = frozenset(self.tixGetEnemyFleetSystem())

        # Get a list of known systems that have not been explored yet.

        setSystemUnexplored = set(oFoUniverse.systemIDs).difference(oFoEmpire.exploredSystemIDs)
        setSystemUnexploredTargeted = set()

        for ixShip in self.tixGetMovingShip(self.tixGetOwnScoutShip()):
            oFoShip = oFoUniverse.getShip(ixShip)

            # If a scout ship is moving to a system, the system is either already explored, or about to be explored.
            # @todo Check if the route is still free from enemy ships.

            setSystemUnexploredTargeted.add(oFoUniverse.getFleet(oFoShip.fleetID).finalDestinationID)

        for ixShip in self.tixGetIdleShip(self.tixGetOwnScoutShip()):
            oFoShip = oFoUniverse.getShip(ixShip)

            # The scout ship is supposed to be located in a system, not moving.

            oGraphRouter = self.__m_oUniverse.oGetGraphRouter(oFoShip.systemID, CGraphAdvisor(ixEnemyFleetSystemFrozenset))

            # Only consider unexplored systems which are not yet targeted by scout ships.

            # @todo However, it might be possible that another idle scout ship is closer to the unexplored system. Try
            # to find the closest idle scout ship first (search by system), and then give orders.

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

                # @todo It is possible that due to a blocked system, the path leaves the supply area and the fleet is
                # lost without fuel outside the supply area.

                for ixSystem in ixSystemList:
                    print(
                        'Ordering fleet %d to move to system %d with result %d (append).' % (
                            oFoShip.fleetID,
                            ixSystem,
                            self.fo.appendFleetMoveOrder(oFoShip.fleetID, ixSystem)
                        )
                    )

        listColonisation = []

        for tupleColonisation in self.__m_oColonisationManager.listGetColonisation():
            if (tupleColonisation[0] in oFoEmpire.fleetSupplyableSystemIDs):
                listColonisation.append(tupleColonisation)

        print(listColonisation)

        setSystemColonisationTargeted = set()

        for ixShip in self.tixGetMovingShip(self.tixGetOwnOutpostShip()):
            oFoShip = oFoUniverse.getShip(ixShip)

            # An outpost ship is on a mission to create an outpost.
            # @todo Check if the route is still free from enemy ships.

            setSystemColonisationTargeted.add(oFoUniverse.getFleet(oFoShip.fleetID).finalDestinationID)

        # Before checking where to move an idle outpost ship to, check if the current system is suitable for
        # colonisation.

        for ixShip in self.tixGetIdleShip(self.tixGetOwnOutpostShip()):
            oFoShip = oFoUniverse.getShip(ixShip)
            ixColoniseSystem = oFoShip.systemID

            if (ixColoniseSystem in setSystemColonisationTargeted):

                # Another outpost ship is already on its way.
                # @todo Use this outpost ship and cancel the other!

                continue

            # @todo If the current system already has a colony that can build outpost bases, do not build an outpost
            # using an outpost ship.

            tupleColonisation = self.__m_oColonisationManager.tupleGetHighestPopulationBySystemColonisation(ixColoniseSystem)

            if (tupleColonisation is not None):

                # In case the fleet is made up of multiple ships, split the ship from the fleet.

                if (not self.bIsSingleShipInFleet(ixShip)):
                    print(
                        'Splitting ship %d from fleet %d with result %d.' % (
                            ixShip,
                            oFoShip.fleetID,
                            self.fo.issueNewFleetOrder(oFoShip.design.name, ixShip)
                        )
                    )

                setSystemColonisationTargeted.add(ixColoniseSystem)

                print(
                    'Ordering ship %d to colonise planet %d with result %d.' % (
                        ixShip,
                        tupleColonisation[1],
                        self.fo.issueColonizeOrder(ixShip, tupleColonisation[1])
                    )
                )

        # Try to find a suitable system somewhere else.

        for ixShip in self.tixGetIdleShip(self.tixGetOwnOutpostShip()):
            if (not listColonisation):

                # There are no further colonisation targets.

                break

            oFoShip = oFoUniverse.getShip(ixShip)

            # The outpost ship is supposed to be located in a system, not moving.

            oGraphRouter = self.__m_oUniverse.oGetGraphRouter(oFoShip.systemID, CGraphAdvisor(ixEnemyFleetSystemFrozenset))

            # Only consider systems which are not yet targeted by outpost ships.

            # @todo However, it might be possible that another idle outpost ship is closer to the system. Try to find
            # the closest idle outpost ship first (search by system), and then give orders.

            for tupleColonisation in listColonisation[:]:
                ixColoniseSystem = tupleColonisation[0]

                if (ixColoniseSystem in setSystemColonisationTargeted):

                    # Another outpost ship is already on its way.

                    continue

                ixSystemList = oGraphRouter.tixGetPath(ixColoniseSystem)

                if (ixSystemList is None):

                    # The outpost ship cannot reach the system.

                    continue

                # In case the fleet is made up of multiple ships, split the ship from the fleet.

                if (not self.bIsSingleShipInFleet(ixShip)):
                    print(
                        'Splitting ship %d from fleet %d with result %d.' % (
                            ixShip,
                            oFoShip.fleetID,
                            self.fo.issueNewFleetOrder(oFoShip.design.name, ixShip)
                        )
                    )

                setSystemColonisationTargeted.add(ixColoniseSystem)
                listColonisation.remove(tupleColonisation)

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

                break


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


    def tixGetOwnOutpostShip(self):
        for ixShip in self.tixGetOwnShipWithPart('CO_OUTPOST_POD'):
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
        for oFleet in self.__m_oFleetHandler.toGetFleet():
            if (not self.__m_oEmpireRelation.bIsOwnFleet(oFleet)):
                if (oFleet.bIsStationary()):
                    yield oFleet.ixGetSystem()
                elif (oFleet.bIsMoving()):
                    yield oFleet.ixGetFinalSystem()


    def bIsSingleShipInFleet(self, ixShip):
        oFoUniverse = self.fo.getUniverse()

        return oFoUniverse.getFleet(oFoUniverse.getShip(ixShip).fleetID).numShips == 1
