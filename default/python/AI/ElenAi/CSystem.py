"""
This is a representation of a system.
"""

from __future__ import print_function


class CSystem(object):


    def __init__(self, ixSystem, fX, fY, iStarType):
        self.__m_ixSystem = ixSystem
        self.__m_fX = fX
        self.__m_fY = fY
        self.__m_iStarType = iStarType

        self.__m_dictPlanet = dict()


    def ixGetSystem(self):
        return self.__m_ixSystem


    def fGetX(self):
        return self.__m_fX


    def fGetY(self):
        return self.__m_fY


    def iGetStarType(self):
        return self.__m_iStarType


    def vAddPlanet(self, oPlanet):
        self.__m_dictPlanet[oPlanet.ixGetPlanet()] = oPlanet

        oPlanet.vSetSystem(self)


    def oGetPlanet(self, ixPlanet):
        return self.__m_dictPlanet[ixPlanet]


    def toGetPlanet(self):
        for ixPlanet, oPlanet in self.__m_dictPlanet.items():
            yield oPlanet


    def vDump(self):
        print(
            'System %d is located at %.3f, %.3f and has star type %d.' % (
                self.ixGetSystem(),
                self.fGetX(),
                self.fGetY(),
                self.iGetStarType()
            )
        )

        for oPlanet in self.toGetPlanet():
            oPlanet.vDump()
