"""
This is a factory to convert a FreeOrion system representation to an abstract representation.
"""

from ElenAi.CSystem import CSystem


class CSystemConverter(object):


    def __init__(self, oFoSystem):
        self.__m_oFoSystem = oFoSystem


    def oGetSystem(self):
        return CSystem(self.__m_oFoSystem.x, self.__m_oFoSystem.y)
