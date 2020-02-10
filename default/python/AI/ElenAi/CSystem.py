"""
This is a representation of a system.
"""


class CSystem(object):


    def __init__(self, ixSystem, fX, fY):
        self.__m_ixSystem = ixSystem
        self.__m_fX = fX
        self.__m_fY = fY


    def ixGetSystem(self):
        return self.__m_ixSystem


    def fGetX(self):
        return self.__m_fX


    def fGetY(self):
        return self.__m_fY
