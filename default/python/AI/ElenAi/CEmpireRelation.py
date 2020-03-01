"""
Manage information about empire relations.
"""


class CEmpireRelation(object):


    def __init__(self, ixOwnEmpire):

        # @todo Add information about war, peace, and alliances.

        self.__m_ixOwnEmpire = ixOwnEmpire


    def bIsOwnPlanet(self, oPlanet):
        """
        Check whether the planet belongs to our own empire.
        """

        return oPlanet.ixGetEmpire() == self.__m_ixOwnEmpire


    def bIsFriendlyPlanet(self, oPlanet):
        """
        Check whether the planet belongs to our own empire, or to any empire at peace (including allies).
        """

        # @todo Implement!

        return self.bIsOwnPlanet(oPlanet)


    def bIsAlliedPlanet(self, oPlanet):
        """
        Check whether the planet belongs to our own empire, or to any allied empire.
        """

        # @todo Implement!

        return self.bIsOwnPlanet(oPlanet)


    def bIsOwnFleet(self, oFleet):
        """
        Check whether the fleet belongs to our own empire.
        """

        return oFleet.ixGetEmpire() == self.__m_ixOwnEmpire


    def bIsFriendlyFleet(self, oFleet):
        """
        Check whether the fleet belongs to our own empire, or to any empire at peace (including allies).
        """

        # @todo Implement!

        return self.bIsOwnFleet(oFleet)


    def bIsAlliedFleet(self, oFleet):
        """
        Check whether the fleet belongs to our own empire, or to any allied empire.
        """

        # @todo Implement!

        return self.bIsOwnFleet(oFleet)
