"""
Predict the capabilities of a whole fleet.
"""

from ElenAi.CShipPredictor import CShipPredictor


class CFleetPredictor(object):


    def __init__(self, oFleet):
        self.__m_oFleet = oFleet


    def bIsArmed(self):
        for oShip in self.__m_oFleet.toGetShip():
            if (CShipPredictor(oShip).bIsArmed()):
                return True

        return False


    def fGetDamage(self):
        fDamage = 0.0

        for oShip in self.__m_oFleet.toGetShip():
            fDamage += CShipPredictor(oShip).fGetDamage()

        return fDamage


    def fGetMaxShield(self):
        """
        Return the largest shield value of any ship inside the fleet.
        """

        # @todo Do not use this value for checking combats. Also consider shield reduction effects like ion storms!

        fMaxShield = 0.0

        for oShip in self.__m_oFleet.toGetShip():
            fMaxShield = max(fMaxShield, CShipPredictor(oShip).fGetShield())

        return fMaxShield


    def fGetMaxStructure(self):
        """
        Return the total structure of all ships in the fleet when fully repaired.
        """

        fMaxStructure = 0.0

        for oShip in self.__m_oFleet.toGetShip():
            fMaxStructure += CShipPredictor(oShip).fGetMaxStructure()

        return fMaxStructure
