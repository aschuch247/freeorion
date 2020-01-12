"""
This is the research manager.
"""

from ElenAi.CManager import CManager
from ElenAi.CResearchTree import CResearchTree


class CResearchManager(CManager):


    def __init__(self, fo, oResearchQueue):
        super(CResearchManager, self).__init__(fo)

        self.m_oResearchQueue = oResearchQueue


    def vManage(self):
        oResearchTree = self.oGetResearchTree()

        # @todo Add the pre-warp technologies here!

        self.vResearch(oResearchTree, 'LRN_PHYS_BRAIN')
        self.vResearch(oResearchTree, 'GRO_SUBTER_HAB')
        self.vResearch(oResearchTree, 'PRO_SENTIENT_AUTOMATION')

    def oGetResearchTree(self):
        oResearchTree = CResearchTree()

        for ixTechnology, sTechnology in enumerate(self.fo.techs()):

            # @todo No research costs are considered right now: 'researchCost()', 'researchTime()', 'perTurnCost()'!

            oResearchTree.vAddTechnology(ixTechnology, sTechnology)

        for sTechnology in self.fo.techs():
            oFoTechnology = self.fo.getTech(sTechnology)

            for sTechnologyPrerequiste in oFoTechnology.prerequisites:
                oResearchTree.vLinkTechnology(
                    oResearchTree.ixGetTechnology(sTechnology),
                    oResearchTree.ixGetTechnology(sTechnologyPrerequiste)
                )

        return oResearchTree


    def bIsResearched(self, sTechnology):
        return self.fo.getEmpire().techResearched(sTechnology)


    def vResearch(self, oResearchTree, sTechnology):
        oGraphRouter = oResearchTree.oGetGraphRouter(oResearchTree.ixGetTechnology(sTechnology))

        for ixTechnology in oGraphRouter.tixGetReachableGraphNode():
            sTechnology = oResearchTree.sGetTechnology(ixTechnology)

            if (not self.bIsResearched(sTechnology)):
                if (not self.m_oResearchQueue.bIsEnqueued(sTechnology)):
                    self.m_oResearchQueue.vEnqueue(sTechnology)
