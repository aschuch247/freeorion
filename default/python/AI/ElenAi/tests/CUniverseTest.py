import unittest

from ElenAi.CSystem import CSystem
from ElenAi.CUniverse import CUniverse


class CUniverseTest(unittest.TestCase):
    def test_CUniverse(self):
        oUniverse = CUniverse()

        oUniverse.vAddSystem(1, CSystem(1.0, 3.0))
        oUniverse.vAddSystem(2, CSystem(4.0, 7.0))

        oUniverse.vLinkSystem(1, 2)

        self.assertEqual(5.0, oUniverse.fGetStarlaneDistance([1, 2]))
