"""
This is a factory to convert a FreeOrion planet representation to an abstract representation.
"""

from ElenAi.CPlanet import CPlanet


class CPlanetConverter(object):


    def __init__(self, oFoPlanet):
        self.__m_oFoPlanet = oFoPlanet


    def oGetPlanet(self):
        return CPlanet(
            self.__m_oFoPlanet.id,
            self.__m_oFoPlanet.speciesName
        )
