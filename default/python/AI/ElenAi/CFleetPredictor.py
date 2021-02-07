"""
Predict the capabilities of a whole fleet.
"""

from ElenAi.CShipDesign import CShipDesign


class CFleetPredictor(object):


    def __init__(self, oDataRepository, oFleet):
        self.__m_oDataRepository = oDataRepository
        self.__m_oFleet = oFleet


    def __oGetShipDesign(self, oShip):
        return CShipDesign(self.__m_oDataRepository, oShip.sGetHull(), oShip.sGetPartList())


    def bIsArmed(self):
        for oShip in self.__m_oFleet.toGetShip():
            if (self.__oGetShipDesign(oShip).bIsArmed()):
                return True

        return False


    def fGetDamage(self):
        fDamage = 0.0

        for oShip in self.__m_oFleet.toGetShip():
            fDamage += self.__oGetShipDesign(oShip).fGetDamage()

        return fDamage


    def fGetMaxDetection(self):
        """
        Return the largest detection range of any ship inside the fleet.
        """

        # @todo Also consider detection range change effects like ion storms!

        fMaxDetection = 0.0

        for oShip in self.__m_oFleet.toGetShip():
            fMaxDetection = max(fMaxDetection, self.__oGetShipDesign(oShip).fGetDetection())

        return fMaxDetection


    def fGetMaxShield(self):
        """
        Return the maximum shield strength of any ship inside the fleet.
        """

        # @todo Do not use this value for checking combats. Use the individual ship shield strength instead.
        # Also consider shield strength change effects like molecular clouds!

        fMaxShield = 0.0

        for oShip in self.__m_oFleet.toGetShip():
            fMaxShield = max(fMaxShield, self.__oGetShipDesign(oShip).fGetShield())

        return fMaxShield


    def fGetMaxStructure(self):
        """
        Return the total structure of all ships in the fleet when fully repaired.
        """

        fMaxStructure = 0.0

        for oShip in self.__m_oFleet.toGetShip():
            fMaxStructure += self.__oGetShipDesign(oShip).fGetMaxStructure()

        return fMaxStructure


    def fGetSpeed(self):
        """
        Return the speed of the fleet. This is the minimum speed of any ship inside the fleet.
        """

        fSpeed = 0.0
        bFirstShip = True

        for oShip in self.__m_oFleet.toGetShip():
            if (bFirstShip):
                fSpeed = self.__oGetShipDesign(oShip).fGetSpeed()
                bFirstShip = False
            else:
                fSpeed = min(fSpeed, self.__oGetShipDesign(oShip).fGetSpeed())

        return fSpeed


    def fGetMinStealth(self):
        """
        Return the minimum stealth strength of any ship inside the fleet.
        """

        fMinStealth = 0.0
        bFirstShip = True

        for oShip in self.__m_oFleet.toGetShip():
            if (bFirstShip):
                fMinStealth = self.__oGetShipDesign(oShip).fGetStealth()
                bFirstShip = False
            else:
                fMinStealth = min(fMinStealth, self.__oGetShipDesign(oShip).fGetStealth())

        return fMinStealth
