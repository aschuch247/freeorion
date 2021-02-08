import unittest

from ElenAi.CDataRepository import CDataRepository
from ElenAi.CFleet import CFleet
from ElenAi.CFleetPredictor import CFleetPredictor
from ElenAi.CShip import CShip
from ElenAi.CShipHullDataStatic import CShipHullDataStatic
from ElenAi.CShipPartDataStatic import CShipPartDataStatic


class CFleetPredictorTest(unittest.TestCase):


    def __oGetDataRepository(self):
        return CDataRepository(
            CShipHullDataStatic(),
            CShipPartDataStatic()
        )


    def test_CFleetPredictor_InitialFleet(self):
        oFleet = CFleet(1, 1, 1, 1, 0.0)

        oFleet.vAddShip(
            CShip(
                1,
                'SP_SCYLIOR',
                'SH_BASIC_SMALL',
                ['DT_DETECTOR_1']
            )
        )

        oFleet.vAddShip(
            CShip(
                2,
                'SP_SCYLIOR',
                'SH_BASIC_SMALL',
                ['DT_DETECTOR_1']
            )
        )

        oFleet.vAddShip(
            CShip(
                3,
                'SP_SCYLIOR',
                'SH_BASIC_MEDIUM',
                ['SR_WEAPON_1_1', 'AR_STD_PLATE', 'FU_BASIC_TANK']
            )
        )

        oFleet.vAddShip(
            CShip(
                4,
                'SP_SCYLIOR',
                'SH_BASIC_MEDIUM',
                ['CO_COLONY_POD']
            )
        )

        oFleetPredictor = CFleetPredictor(self.__oGetDataRepository(), oFleet)

        self.assertEqual(True, oFleetPredictor.bIsArmed())
        self.assertEqual(3.0, oFleetPredictor.fGetDamage())
        # @todo self.assertEqual(50.0, oFleetPredictor.fGetMaxDetection())
        self.assertEqual(0.0, oFleetPredictor.fGetMaxShield())
        self.assertEqual(36.0, oFleetPredictor.fGetMaxStructure())
        self.assertEqual(60.0, oFleetPredictor.fGetSpeed())
        self.assertEqual(5.0, oFleetPredictor.fGetMinStealth())
