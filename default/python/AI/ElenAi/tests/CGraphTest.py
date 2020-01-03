import unittest

from ElenAi.CGraph import CGraph


class CGraphTest(unittest.TestCase):


    def test_CGraph_fGetCost(self):
        oGraph = CGraph()

        oGraph.vAdd(1)
        oGraph.vAdd(2)
        oGraph.vAdd(3)

        oGraph.vLink(1, 2, 10.0)
        oGraph.vLink(2, 3, 2.0)

        self.assertEqual(0.0, oGraph.fGetCost([]))
        self.assertEqual(0.0, oGraph.fGetCost([1]))
        self.assertEqual(12.0, oGraph.fGetCost([1, 2, 3]))


    def test_CGraph_oGetGraphRouting_possible(self):
        oGraph = CGraph()

        oGraph.vAdd(1)
        oGraph.vAdd(2)
        oGraph.vAdd(3)
        oGraph.vAdd(4)
        oGraph.vAdd(5)
        oGraph.vAdd(6)

        oGraph.vLink(1, 2, 10.0)
        oGraph.vLink(1, 3, 1.0)
        oGraph.vLink(3, 5, 1.0)
        oGraph.vLink(5, 6, 1.0)
        oGraph.vLink(6, 4, 1.0)
        oGraph.vLink(4, 2, 1.0)

        oGraphRouter = oGraph.oGetGraphRouter(1)
        tixPath = oGraphRouter.tixGetPath(2)

        self.assertEqual([1, 3, 5, 6, 4, 2], tixPath)
        self.assertEqual(5.0, oGraph.fGetCost(tixPath))


    def test_CGraph_oGetGraphRouting_impossible(self):
        oGraph = CGraph()

        oGraph.vAdd(1)
        oGraph.vAdd(2)

        oGraphRouter = oGraph.oGetGraphRouter(1)
        tixPath = oGraphRouter.tixGetPath(2)

        self.assertEqual(None, tixPath)
