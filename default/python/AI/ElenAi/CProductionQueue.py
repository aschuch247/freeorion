"""
This class contains methods to manage the production queue of the empire.
"""

from __future__ import print_function


class CProductionQueue(object):


    def __init__(self, fo):
        self.fo = fo


    def bIsEnqueuedBuilding(self, ixPlanet, sBuilding):
        for oFoProductionQueueElement in self.fo.getEmpire().productionQueue:
            if (oFoProductionQueueElement.locationID == ixPlanet):
                if (oFoProductionQueueElement.buildType == self.fo.buildType.building):
                    if (oFoProductionQueueElement.name == sBuilding):
                        return True

        return False


    def bIsEnqueuedShipDesign(self, ixPlanet, ixShipDesign):
        for oFoProductionQueueElement in self.fo.getEmpire().productionQueue:
            if (oFoProductionQueueElement.locationID == ixPlanet):
                if (oFoProductionQueueElement.buildType == self.fo.buildType.ship):
                    if (oFoProductionQueueElement.designID == ixShipDesign):
                        return True

        return False


    def vEnqueueBuilding(self, ixPlanet, sBuilding):
        print(
            'Enqueuing building \'%s\' at planet \'%s\', system \'%s\' with result %d.' % (
                sBuilding,
                self.fo.getUniverse().getPlanet(ixPlanet).name,
                self.fo.getUniverse().getSystem(self.fo.getUniverse().getPlanet(ixPlanet).systemID).name,
                self.fo.issueEnqueueBuildingProductionOrder(sBuilding, ixPlanet)
            )
        )


    def vEnqueueShipDesign(self, ixPlanet, ixShipDesign):
        print(
            'Enqueuing ship design \'%s\' at planet \'%s\', system \'%s\' with result %d.' % (
                self.fo.getShipDesign(ixShipDesign).name,
                self.fo.getUniverse().getPlanet(ixPlanet).name,
                self.fo.getUniverse().getSystem(self.fo.getUniverse().getPlanet(ixPlanet).systemID).name,
                self.fo.issueEnqueueShipProductionOrder(ixShipDesign, ixPlanet)
            )
        )


    def vLog(self):
        print('--- production queue ---')

        for oFoProductionQueueElement in self.fo.getEmpire().productionQueue:
            oFoPlanet = self.fo.getUniverse().getPlanet(oFoProductionQueueElement.locationID)

            if (oFoProductionQueueElement.buildType == self.fo.buildType.ship):
                print(
                    'ship design \'%s\' (planet \'%s\', system \'%s\')' % (
                        self.fo.getShipDesign(oFoProductionQueueElement.designID).name,
                        oFoPlanet.name,
                        self.fo.getUniverse().getSystem(oFoPlanet.systemID).name,
                    )
                )
            elif (oFoProductionQueueElement.buildType == self.fo.buildType.building):
                print(
                    'building \'%s\' (planet \'%s\', system \'%s\')' % (
                        oFoProductionQueueElement.name,
                        oFoPlanet.name,
                        self.fo.getUniverse().getSystem(oFoPlanet.systemID).name,
                    )
                )
