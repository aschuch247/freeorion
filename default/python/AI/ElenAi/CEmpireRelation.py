"""
Manage information about empire relations.
"""


class CEmpireRelation(object):


    def __init__(self, ixOwnEmpire):
        """
        @todo Add information about war, peace, and alliances.
        """

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


    def bIsOwnFleet(self, oFleet):
        return oFleet.ixGetEmpire() == self.__m_ixOwnEmpire
