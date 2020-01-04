import unittest

from ElenAi.CGraphAdvisor import CGraphAdvisor
from ElenAi.CResearchTree import CResearchTree


class CResearchTreeTest(unittest.TestCase):
    def test_CResearchTree(self):
        oResearchTree = CResearchTree()

        oResearchTree.vAddTechnology(1, 'GRO_GENETIC_ENG')
        oResearchTree.vAddTechnology(2, 'GRO_PLANET_ECOL')
        oResearchTree.vAddTechnology(3, 'GRO_SUBTER_HAB')
        oResearchTree.vAddTechnology(4, 'GRO_ADV_ECOMAN')
        oResearchTree.vAddTechnology(5, 'GRO_SYMBIOTIC_BIO')
        oResearchTree.vAddTechnology(6, 'GRO_LIFECYCLE_MAN')
        oResearchTree.vAddTechnology(7, 'GRO_GENETIC_MED')
        oResearchTree.vAddTechnology(8, 'GRO_XENO_GENETICS')

        oResearchTree.vLinkTechnology(3, 2)
        oResearchTree.vLinkTechnology(4, 3)
        oResearchTree.vLinkTechnology(5, 2)
        oResearchTree.vLinkTechnology(6, 1)
        oResearchTree.vLinkTechnology(7, 1)
        oResearchTree.vLinkTechnology(8, 5)
        oResearchTree.vLinkTechnology(8, 7)

        oGraphRouter = oResearchTree.oGetGraphRouter(4)

        self.assertEqual([2, 3, 4], list(oGraphRouter.tixGetReachableGraphNode()))


    def test_CResearchTree_gained_technology(self):
        """
        It is possible to get technologies from other sources. If the empire has 'SHP_WEAPON_4_1', the empire can
        research 'SHP_WEAPON_4_2', without having the prerequistes for 'SHP_WEAPON_4_1'.
        """

        oResearchTree = CResearchTree()

        oResearchTree.vAddTechnology(1, 'GRO_GENETIC_ENG')
        oResearchTree.vAddTechnology(2, 'GRO_PLANET_ECOL')
        oResearchTree.vAddTechnology(3, 'GRO_SUBTER_HAB')
        oResearchTree.vAddTechnology(4, 'GRO_ADV_ECOMAN')
        oResearchTree.vAddTechnology(5, 'GRO_SYMBIOTIC_BIO')
        oResearchTree.vAddTechnology(6, 'GRO_LIFECYCLE_MAN')
        oResearchTree.vAddTechnology(7, 'GRO_GENETIC_MED')
        oResearchTree.vAddTechnology(8, 'GRO_XENO_GENETICS')

        oResearchTree.vLinkTechnology(3, 2)
        oResearchTree.vLinkTechnology(4, 3)
        oResearchTree.vLinkTechnology(5, 2)
        oResearchTree.vLinkTechnology(6, 1)
        oResearchTree.vLinkTechnology(7, 1)
        oResearchTree.vLinkTechnology(8, 5)
        oResearchTree.vLinkTechnology(8, 7)

        # Here, we claim to know 'GRO_SYMBIOTIC_BIO'.

        oGraphRouter = oResearchTree.oGetGraphRouter(8, CGraphAdvisor({5}))

        self.assertEqual([1, 7, 8], list(oGraphRouter.tixGetReachableGraphNode()))
