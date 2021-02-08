"""
This is a data repository.
"""


class CDataRepository(object):


    def __init__(self, oShipHullData, oShipPartData):
        self.__m_oShipHullData = oShipHullData
        self.__m_oShipPartData = oShipPartData


    def oGetShipHullData(self):
        return self.__m_oShipHullData


    def oGetShipPartData(self):
        return self.__m_oShipPartData
