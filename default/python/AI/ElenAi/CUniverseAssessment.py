"""
Assess the universe.
"""


class CUniverseAssessment(object):
    def __init__(self, fo):
        self.fo = fo

    def vAssessUniverse(self):
        oFoUniverse = self.fo.getUniverse()

        for systemId in oFoUniverse.systemIDs:
            oFoSystem = oFoUniverse.getSystem(systemId)
            # print 'I know system %s (%d).' % (oFoSystem.name, oFoSystem.systemID)

            if (oFoSystem.numWormholes != 0):
                print 'Wormholes found!'

        oFoEmpire = self.fo.getEmpire()

        for systemId in oFoEmpire.exploredSystemIDs:
            oFoSystem = oFoUniverse.getSystem(systemId)
            # print 'I have explored system %s (%d).' % (oFoSystem.name, oFoSystem.systemID)

        # Get a list of known systems that have not been explored yet.

        unexploredSystemId = -1;

        for systemId in set(oFoUniverse.systemIDs).difference(oFoEmpire.exploredSystemIDs):
            oFoSystem = oFoUniverse.getSystem(systemId)
            # print 'I have not yet explored system %s (%d).' % (oFoSystem.name, oFoSystem.systemID)
            unexploredSystemId = systemId

        if unexploredSystemId != -1:

            # This code will send all idle fleets to the same system. Mark a system with the proper incoming fleet.

            for fleetId in oFoUniverse.fleetIDs:
                oFoFleet = oFoUniverse.getFleet(fleetId)

                if oFoFleet.ownedBy(self.fo.empireID()):
                    if (oFoFleet.finalDestinationID == -1) or (oFoFleet.finalDestinationID == oFoFleet.systemID):

                        # The fleet has no orders yet or any more.

                        self.fo.issueFleetMoveOrder(fleetId, unexploredSystemId)
