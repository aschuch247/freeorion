"""
This is a factory to convert a FreeOrion planet representation to an abstract representation.
"""

from freeOrionAIInterface import meterType

from ElenAi.CPlanet import CPlanet


class CPlanetConverter(object):


    def __init__(self, oFoPlanet):
        self.__m_oFoPlanet = oFoPlanet


    def oGetPlanet(self):
        return CPlanet(
            self.__m_oFoPlanet.id,
            self.__m_oFoPlanet.owner,
            self.__m_oFoPlanet.speciesName,
            self.__m_oFoPlanet.initialMeterValue(meterType.population)
        )
