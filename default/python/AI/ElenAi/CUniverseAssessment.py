"""
Assess the universe.
"""


class CUniverseAssessment(object):
    def __init__(self, fo):
        self.fo = fo

    def vAssessUniverse(self):
        oUniverse = self.fo.getUniverse()

        for systemId in oUniverse.systemIDs:
            oSystem = oUniverse.getSystem(systemId)
            print 'I know system %s (%d).' % (oSystem.name, oSystem.systemID)

            if (oSystem.numWormholes != 0):
                print 'Wormholes found!'

        oEmpire = self.fo.getEmpire()

        for systemId in oEmpire.exploredSystemIDs:
            oSystem = oUniverse.getSystem(systemId)
            print 'I have explored system %s (%d).' % (oSystem.name, oSystem.systemID)

        # Get a list of known systems that have not been explored yet.

        unexploredSystemId = -1;

        for systemId in set(oUniverse.systemIDs).difference(oEmpire.exploredSystemIDs):
            oSystem = oUniverse.getSystem(systemId)
            print 'I have not yet explored system %s (%d).' % (oSystem.name, oSystem.systemID)
            unexploredSystemId = systemId

        if unexploredSystemId != -1:

            # This code will send all idle fleets to the same system. Mark a system with the proper incoming fleet.

            for fleetId in oUniverse.fleetIDs:
                oFleet = oUniverse.getFleet(fleetId)

                if oFleet.ownedBy(self.fo.empireID()):
                    if (oFleet.finalDestinationID == -1) or (oFleet.finalDestinationID == oFleet.systemID):

                        # The fleet has no orders yet or any more.

                        self.fo.issueFleetMoveOrder(fleetId, unexploredSystemId)
