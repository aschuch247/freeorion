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


    def fGetMaxDetection(self):
        """
        Return the largest detection range of any ship inside the fleet.
        """

        # @todo Also consider detection range change effects like ion storms!

        fMaxDetection = 0.0

        for oShip in self.__m_oFleet.toGetShip():
            fMaxDetection = max(fMaxDetection, CShipPredictor(oShip).fGetDetection())

        return fMaxDetection


    def fGetMaxShield(self):
        """
        Return the largest shield strength of any ship inside the fleet.
        """

        # @todo Do not use this value for checking combats. Use the individual ship shield strength instead.
        # Also consider shield strength change effects like molecular clouds!

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


    def fGetSpeed(self):
        """
        Return the speed of the fleet. This is the minimum speed of any ship inside the fleet.
        """

        fSpeed = 0.0
        bFirstShip = True

        for oShip in self.__m_oFleet.toGetShip():
            if (bFirstShip):
                fSpeed = CShipPredictor(oShip).fGetSpeed()
                bFirstShip = False
            else:
                fSpeed = min(fSpeed, CShipPredictor(oShip).fGetSpeed())

        return fSpeed
