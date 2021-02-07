import unittest

from ElenAi.Constant.CStarType import CStarType
from ElenAi.CSystem import CSystem
from ElenAi.CUniverse import CUniverse


class CUniverseTest(unittest.TestCase):


    def test_CUniverse(self):
        oUniverse = CUniverse()

        oUniverse.vAddSystem(CSystem(1, 1.0, 3.0, CStarType.blue))
        oUniverse.vAddSystem(CSystem(2, 4.0, 7.0, CStarType.blue))
        oUniverse.vAddSystem(CSystem(3, 9.0, 19.0, CStarType.blue))

        oUniverse.vLinkSystem(1, 2)
        oUniverse.vLinkSystem(2, 1)
        oUniverse.vLinkSystem(2, 3)
        oUniverse.vLinkSystem(3, 2)

        self.assertEqual(18.0, oUniverse.fGetCost([1, 2, 3]))
        self.assertEqual(18.0, oUniverse.fGetCost([3, 2, 1]))
