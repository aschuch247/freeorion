"""
Manage information about empire relations.
"""


class CEmpireRelation(object):


    def __init__(self, ixOwnEmpire):
        self.__m_ixOwnEmpire = ixOwnEmpire


    def bIsOwnPlanet(self, oPlanet):
        """
        Check whether the planet belongs to our own empire.
        """

        return oPlanet.ixGetEmpire() == self.__m_ixOwnEmpire


    def bIsFriendlyPlanet(self, oPlanet):
        """
        Check whether the planet belongs to any friendly empire.
        """

        return self.bIsOwnPlanet()
