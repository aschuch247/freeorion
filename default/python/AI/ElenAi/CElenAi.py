"""
This is ElenAI, an AI module.
"""

from ElenAi.CUniverseAssessment import CUniverseAssessment


class CElenAi(object):
    def vAssessUniverse(self, fo):
        oUniverseAssessment = CUniverseAssessment(fo)
        oUniverseAssessment.vAssessUniverse()
        return
