"""
This is a representation of a planet.
"""


class CPlanet(object):


    def __init__(self, ixPlanet):
        self.__m_ixPlanet = ixPlanet

        self.__m_oSystem = None


    def ixGetPlanet(self):
        return self.__m_ixPlanet


    def vSetSystem(self, oSystem):
        self.__m_oSystem = oSystem


    def oGetSystem(self):
        return self.__m_oSystem
