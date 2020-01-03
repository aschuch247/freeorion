"""
This is ElenAI, an AI module.
"""

from ElenAi.CColonyManager import CColonyManager
from ElenAi.CFleetManager import CFleetManager
from ElenAi.CResearchManager import CResearchManager
from ElenAi.CResearchQueue import CResearchQueue
from ElenAi.CProductionQueue import CProductionQueue
from ElenAi.CUniverseAssessment import CUniverseAssessment


class CElenAi(object):
    def vGenerateOrders(self, fo):
        oUniverseAssessment = CUniverseAssessment(fo)
        oUniverseAssessment.vAssessUniverse()

        oColonyManager = CColonyManager(fo)
        oColonyManager.vManage()

        oFleetManager = CFleetManager(fo)
        oFleetManager.vManage()

        oResearchManager = CResearchManager(fo)
        oResearchManager.vManage()

        oProductionQueue = CProductionQueue(fo)
        oProductionQueue.vLog()

        oResearchQueue = CResearchQueue(fo)
        oResearchQueue.vLog()

        return
