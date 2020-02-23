"""
This is a representation of a fleet.
"""

from __future__ import print_function


class CFleet(object):


    def __init__(self, ixFleet, ixEmpire):
        self.__m_ixFleet = ixFleet
        self.__m_ixEmpire = ixEmpire

        self.__m_dictShip = dict()


    def ixGetFleet(self):
        return self.__m_ixFleet


    def ixGetEmpire(self):
        """
        Return the empire that owns the fleet. The value can be negative in case the fleet is not owned by any empire.
        The empire identifier 0 seems to be unused.
        """

        return self.__m_ixEmpire


    def bIsOwned(self):
        """
        Return whether the fleet is owned by any empire.
        """

        return self.__m_ixEmpire >= 0


    def bIsMonster(self):
        """
        Indicate whether the fleet is a space monster.
        """

        return not self.bIsOwned()


    def vAddShip(self, oShip):
        self.__m_dictShip[oShip.ixGetShip()] = oShip

        oShip.vSetFleet(self)


    def oGetShip(self, ixShip):
        return self.__m_dictShip[ixShip]


    def toGetShip(self):
        for ixShip, oShip in self.__m_dictShip.items():
            yield oShip


    def vDump(self):
        if (self.bIsMonster()):
            print(
                'Fleet %d is a space monster.' % (
                    self.ixGetFleet()
                )
            )
        else:
            print(
                'Fleet %d is owned by empire %d.' % (
                    self.ixGetFleet(),
                    self.ixGetEmpire()
                )
            )

        for oShip in self.toGetShip():
            oShip.vDump()
