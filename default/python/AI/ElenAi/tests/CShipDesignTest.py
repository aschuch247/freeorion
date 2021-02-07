import unittest

from ElenAi.CDataRepository import CDataRepository
from ElenAi.CShipDesign import CShipDesign
from ElenAi.CShipHullDataStatic import CShipHullDataStatic


class CShipDesignTest(unittest.TestCase):


    def __oGetDataRepository(self):
        return CDataRepository(CShipHullDataStatic())


    def test_CShipDesign_InitialBattleShip(self):
        oShipDesign = CShipDesign(
            self.__oGetDataRepository(),
            'SH_BASIC_MEDIUM',
            ['SR_WEAPON_1_1', 'AR_STD_PLATE', 'FU_BASIC_TANK']
        )

        self.assertEqual(True, oShipDesign.bIsArmed())
        self.assertEqual(3.0, oShipDesign.fGetDamage())
        # @todo self.assertEqual(25.0, oShipDesign.fGetDetection())
        self.assertEqual(0.0, oShipDesign.fGetShield())
        self.assertEqual(16.0, oShipDesign.fGetMaxStructure())
        self.assertEqual(60.0, oShipDesign.fGetSpeed())
        self.assertEqual(5.0, oShipDesign.fGetStealth())


    def test_CShipDesign_InitialScout(self):
        oShipDesign = CShipDesign(
            self.__oGetDataRepository(),
            'SH_BASIC_SMALL',
            ['DT_DETECTOR_1']
        )

        self.assertEqual(False, oShipDesign.bIsArmed())
        self.assertEqual(0.0, oShipDesign.fGetDamage())
        # @todo self.assertEqual(50.0, oShipDesign.fGetDetection())
        self.assertEqual(0.0, oShipDesign.fGetShield())
        self.assertEqual(5.0, oShipDesign.fGetMaxStructure())
        self.assertEqual(75.0, oShipDesign.fGetSpeed())
        self.assertEqual(5.0, oShipDesign.fGetStealth())
