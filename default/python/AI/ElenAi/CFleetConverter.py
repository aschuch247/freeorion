"""
This is a factory to convert a FreeOrion fleet representation to an abstract representation.
"""

from ElenAi.CFleet import CFleet


class CFleetConverter(object):


    def __init__(self, oFoFleet):
        self.__m_oFoFleet = oFoFleet


    def oGetFleet(self):
        return CFleet(
            self.__m_oFoFleet.id,
            self.__m_oFoFleet.owner
        )
