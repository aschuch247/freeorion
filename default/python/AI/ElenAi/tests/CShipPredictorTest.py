import unittest

from ElenAi.CShip import CShip
from ElenAi.CShipPredictor import CShipPredictor


class CShipPredictorTest(unittest.TestCase):


    def test_CShipPredictor_InitialBattleShip(self):
        oShip = CShip(
            1,
            'SP_ABADDONI',
            'SH_BASIC_MEDIUM',
            ['SR_WEAPON_1_1', 'AR_STD_PLATE', 'FU_BASIC_TANK']
        )

        oShipPredictor = CShipPredictor(oShip)

        self.assertEqual(True, oShipPredictor.bIsArmed())
        self.assertEqual(3.0, oShipPredictor.fGetDamage())
        self.assertEqual(25.0, oShipPredictor.fGetDetection())
        self.assertEqual(0.0, oShipPredictor.fGetShield())
        self.assertEqual(16.0, oShipPredictor.fGetMaxStructure())
        self.assertEqual(60.0, oShipPredictor.fGetSpeed())
        self.assertEqual(5.0, oShipPredictor.fGetStealth())


    def test_CShipPredictor_InitialScout(self):
        oShip = CShip(
            1,
            'SP_ABADDONI',
            'SH_BASIC_SMALL',
            ['DT_DETECTOR_1']
        )

        oShipPredictor = CShipPredictor(oShip)

        self.assertEqual(False, oShipPredictor.bIsArmed())
        self.assertEqual(0.0, oShipPredictor.fGetDamage())
        self.assertEqual(50.0, oShipPredictor.fGetDetection())
        self.assertEqual(0.0, oShipPredictor.fGetShield())
        self.assertEqual(5.0, oShipPredictor.fGetMaxStructure())
        self.assertEqual(75.0, oShipPredictor.fGetSpeed())
        self.assertEqual(5.0, oShipPredictor.fGetStealth())
