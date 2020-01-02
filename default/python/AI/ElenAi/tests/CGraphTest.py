import unittest

from ElenAi.CGraph import CGraph


class CGraphTest(unittest.TestCase):
    def test_CGraph(self):
        oGraph = CGraph()

        oGraph.vAdd(1)
        oGraph.vAdd(2)
        oGraph.vAdd(3)

        oGraph.vLink(1, 2, 10.0)
        oGraph.vLink(2, 3, 2.0)

        self.assertEqual(0.0, oGraph.fGetCost([]))
        self.assertEqual(0.0, oGraph.fGetCost([1]))
        self.assertEqual(12.0, oGraph.fGetCost([1, 2, 3]))
