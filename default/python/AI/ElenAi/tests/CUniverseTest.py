import unittest

from ElenAi.CSystem import CSystem
from ElenAi.CUniverse import CUniverse


class CUniverseTest(unittest.TestCase):
    def test_CUniverse(self):
        oUniverse = CUniverse()

        oUniverse.vAddSystem(1, CSystem(1.0, 3.0))
        oUniverse.vAddSystem(2, CSystem(4.0, 7.0))
        oUniverse.vAddSystem(3, CSystem(9.0, 19.0))

        oUniverse.vLinkSystem(1, 2)
        oUniverse.vLinkSystem(2, 1)
        oUniverse.vLinkSystem(2, 3)
        oUniverse.vLinkSystem(3, 2)

        self.assertEqual(18.0, oUniverse.fGetCost([1, 2, 3]))
        self.assertEqual(18.0, oUniverse.fGetCost([3, 2, 1]))
