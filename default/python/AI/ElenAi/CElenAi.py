"""
This is ElenAI, an AI module.
"""

from __future__ import print_function

from ElenAi.Adapter.CFleetAdapter import CFleetAdapter
from ElenAi.Adapter.CPlanetAdapter import CPlanetAdapter
from ElenAi.Adapter.CShipAdapter import CShipAdapter
from ElenAi.Adapter.CSystemAdapter import CSystemAdapter
from ElenAi.CColonisationManager import CColonisationManager
from ElenAi.CColonyManager import CColonyManager
from ElenAi.CColonyPredictor import CColonyPredictor
from ElenAi.CDataRepository import CDataRepository
from ElenAi.CEmpireManager import CEmpireManager
from ElenAi.CEmpireRelation import CEmpireRelation
from ElenAi.CFleetHandler import CFleetHandler
from ElenAi.CFleetMovementManager import CFleetMovementManager
from ElenAi.CFleetPredictor import CFleetPredictor
from ElenAi.CFleetProductionManager import CFleetProductionManager
from ElenAi.CProductionQueue import CProductionQueue
from ElenAi.CResearchManager import CResearchManager
from ElenAi.CResearchQueue import CResearchQueue
from ElenAi.CShipHullDataDynamic import CShipHullDataDynamic
from ElenAi.CSpeciesDataDynamic import CSpeciesDataDynamic
from ElenAi.CUniverse import CUniverse


class CElenAi(object):


    def __init__(self, fo):
        self.__m_fo = fo


    def __oGetDataRepository(self):
        return CDataRepository(CShipHullDataDynamic(self.__m_fo))


    def vGenerateOrders(self):
        oUniverse = self.oGetUniverse()
        oFleetHandler = self.oGetFleetHandler()

        # @todo Show turn number and site report.

        oEmpireRelation = CEmpireRelation(self.__m_fo.empireID())
        oEmpireManager = CEmpireManager(oUniverse, oEmpireRelation, self.__m_fo.getEmpire().availableTechs)

        oProductionQueue = CProductionQueue(self.__m_fo)
        oResearchQueue = CResearchQueue(self.__m_fo)

        oColonyPredictor = CColonyPredictor(self.__m_fo.getEmpire().availableTechs)

        oColonisationManager = CColonisationManager(self.__m_fo, oUniverse, oEmpireManager, oEmpireRelation, oColonyPredictor, CSpeciesDataDynamic(self.__m_fo))
        oColonisationManager.vManage()

        oColonyManager = CColonyManager(self.__m_fo, oUniverse, oEmpireManager, oEmpireRelation, oColonisationManager, oProductionQueue, CSpeciesDataDynamic(self.__m_fo))
        oColonyManager.vManage()

        oFleetMovementManager = CFleetMovementManager(self.__m_fo, self.__oGetDataRepository(), oUniverse, oEmpireRelation, oFleetHandler, oColonisationManager)
        oFleetMovementManager.vManage()

        oFleetProductionManager = CFleetProductionManager(self.__m_fo, oProductionQueue)
        oFleetProductionManager.vManage()

        oResearchManager = CResearchManager(self.__m_fo, oResearchQueue)
        oResearchManager.vManage()

        oProductionQueue.vLog()
        oResearchQueue.vLog()


    def oGetUniverse(self):
        oUniverse = CUniverse()
        oFoUniverse = self.__m_fo.getUniverse()

        for ixSystem in oFoUniverse.systemIDs:
            oFoSystem = oFoUniverse.getSystem(ixSystem)
            oSystem = CSystemAdapter(oFoSystem).oGetSystem()

            oUniverse.vAddSystem(oSystem)

            for ixPlanet in oFoSystem.planetIDs:
                oFoPlanet = oFoUniverse.getPlanet(ixPlanet)
                oPlanet = CPlanetAdapter(oFoUniverse, oFoPlanet).oGetPlanet()

                oSystem.vAddPlanet(oPlanet)

        for ixSystem in oFoUniverse.systemIDs:
            for ixSystemNeighbour in oFoUniverse.getImmediateNeighbors(ixSystem, self.__m_fo.empireID()):
                oUniverse.vLinkSystem(ixSystem, ixSystemNeighbour)

        # oUniverse.vDump()

        # The following code is runtime debug code to check if the AI expectations match the server implementation.

        print('--- population expectation checker ---')

        oSpeciesData = CSpeciesDataDynamic(self.__m_fo)

        for oSystem in oUniverse.toGetSystem():
            for oPlanet in oSystem.toGetPlanet():
                if (oPlanet.bIsColony()):
                    oColonyPredictor = CColonyPredictor(self.__m_fo.getEmpire(oPlanet.ixGetEmpire()).availableTechs)
                    oFoPlanet = oFoUniverse.getPlanet(oPlanet.ixGetPlanet())

                    # Assert that the colony maximum population prediction works as expected!

                    fActualMaxPopulation = oFoPlanet.currentMeterValue(self.__m_fo.meterType.targetPopulation)
                    fExpectedMaxPopulation = oColonyPredictor.fGetMaxPopulation(oPlanet, oSpeciesData.oGetSpecies(oPlanet.sGetSpecies()))

                    if (fExpectedMaxPopulation != fActualMaxPopulation):
                        print(
                            'Planet %d is expected to have a colony maximum population of %.2f but actually has a colony maximum population of %.2f!' % (
                                oPlanet.ixGetPlanet(),
                                fExpectedMaxPopulation,
                                fActualMaxPopulation
                            )
                        )

        return oUniverse


    def oGetFleetHandler(self):
        oFleetHandler = CFleetHandler()
        oFoUniverse = self.__m_fo.getUniverse()

        for ixFleet in oFoUniverse.fleetIDs:
            oFoFleet = oFoUniverse.getFleet(ixFleet)
            oFleet = CFleetAdapter(oFoFleet).oGetFleet()

            oFleetHandler.vAddFleet(oFleet)

            for ixShip in oFoFleet.shipIDs:
                oFoShip = oFoUniverse.getShip(ixShip)
                oShip = CShipAdapter(oFoShip).oGetShip()

                oFleet.vAddShip(oShip)

        # oFleetHandler.vDump()

        # The following code is runtime debug code to check if the AI expectations match the server implementation.

        print('--- fleet expectation checker ---')

        for oFleet in oFleetHandler.toGetFleet():
            oFleetPredictor = CFleetPredictor(self.__oGetDataRepository(), oFleet)
            oFoFleet = oFoUniverse.getFleet(oFleet.ixGetFleet())

            # Assert that the fleet categorisation of armed fleets works as expected!

            bActualIsArmed = oFoFleet.hasArmedShips
            bExpectedIsArmed = oFleetPredictor.bIsArmed()

            if (bExpectedIsArmed != bActualIsArmed):
                print(
                    'Fleet %d is expected to be armed (%d) but actually is armed (%d)!' % (
                        oFleet.ixGetFleet(),
                        bExpectedIsArmed,
                        bActualIsArmed
                    )
                )

            # Assert that the fleet damage prediction works as expected!

            fActualDamage = 0.0

            for ixShip in oFoFleet.shipIDs:
                oFoShip = oFoUniverse.getShip(ixShip)

                for sPart in oFoShip.design.parts:
                    fActualDamage += oFoShip.currentPartMeterValue(self.__m_fo.meterType.maxCapacity, sPart)

            fExpectedDamage = oFleetPredictor.fGetDamage()

            if (fExpectedDamage != fActualDamage):
                print(
                    'Fleet %d is expected to inflict %.2f damage but actually can inflict %.2f damage!' % (
                        oFleet.ixGetFleet(),
                        fExpectedDamage,
                        fActualDamage
                    )
                )

            # Assert that the fleet maximum detection range prediction works as expected!

            fActualMaxDetection = 0.0

            for ixShip in oFoFleet.shipIDs:
                fActualMaxDetection = max(fActualMaxDetection, oFoUniverse.getShip(ixShip).currentMeterValue(self.__m_fo.meterType.detection))

            fExpectedMaxDetection = oFleetPredictor.fGetMaxDetection();

            if (fExpectedMaxDetection != fActualMaxDetection):
                print(
                    'Fleet %d is expected to have a fleet maximum detection range of %.2f but actually has a fleet maximum detection range of %.2f!' % (
                        oFleet.ixGetFleet(),
                        fExpectedMaxDetection,
                        fActualMaxDetection
                    )
                )

            # Assert that the fleet maximum shield strength prediction works as expected!

            fActualMaxShield = 0.0

            for ixShip in oFoFleet.shipIDs:
                fActualMaxShield = max(fActualMaxShield, oFoUniverse.getShip(ixShip).currentMeterValue(self.__m_fo.meterType.maxShield))

            fExpectedMaxShield = oFleetPredictor.fGetMaxShield()

            if (fExpectedMaxShield != fActualMaxShield):
                print(
                    'Fleet %d is expected to have a fleet maximum shield strength of %.2f but actually has a fleet maximum shield strength of %.2f!' % (
                        oFleet.ixGetFleet(),
                        fExpectedMaxShield,
                        fActualMaxShield
                    )
                )

            # Assert that the fleet maximum structure prediction works as expected!

            fActualMaxStructure = 0.0

            for ixShip in oFoFleet.shipIDs:
                fActualMaxStructure += oFoUniverse.getShip(ixShip).currentMeterValue(self.__m_fo.meterType.maxStructure)

            fExpectedMaxStructure = oFleetPredictor.fGetMaxStructure()

            if (fExpectedMaxStructure != fActualMaxStructure):
                print(
                    'Fleet %d is expected to have a fleet maximum structure of %.2f but actually has a fleet maximum structure of %.2f!' % (
                        oFleet.ixGetFleet(),
                        fExpectedMaxStructure,
                        fActualMaxStructure
                    )
                )

            # Assert that the fleet speed prediction works as expected!

            fActualSpeed = oFleet.fGetSpeed()
            fExpectedSpeed = oFleetPredictor.fGetSpeed()

            if (fExpectedSpeed != fActualSpeed):
                print(
                    'Fleet %d is expected to have a fleet speed of %.2f but actually has a fleet speed of %.2f!' % (
                        oFleet.ixGetFleet(),
                        fExpectedSpeed,
                        fActualSpeed
                    )
                )

            # @todo Assert that the fleet maximum fuel prediction works as expected! - oFoFleet.maxFuel
            # @todo Assert that the fleet minimum and maximum stealth prediction works as expected!

        return oFleetHandler
