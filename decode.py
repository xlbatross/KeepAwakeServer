from enum import Enum
import numpy as np

class DecodeType(Enum):
    Login = 0
    DrivingImage = 1
    DrowsyCount = 2

class Decode:
    def __init__(self):
        self.type : int = -1
        self.dataBytesList : list[bytearray] = []

class DecodeTCP(Decode):
    def __init__(self, rawData : bytearray):
        super().__init__()
        pointer : int = 0
        headerSize : int = 0
        dataLengthList : list[int] = []

        headerSize = int.from_bytes(rawData[pointer : pointer + 4], "little")
        pointer += 4
        self.type = int.from_bytes(rawData[pointer : pointer + 4], "little")
        pointer += 4

        for i in range(0, headerSize - 4, 4):
            dataLengthList.append(int.from_bytes(rawData[pointer : pointer + 4], "little"))
            pointer += 4
        
        for length in dataLengthList:
            self.dataBytesList.append(rawData[pointer : pointer + length])
            pointer += length

class DcdImage:
    def __init__(self, dcdtcp : DecodeTCP):
        self.rows : int = int.from_bytes(dcdtcp.dataBytesList[0], "little")
        self.cols : int = int.from_bytes(dcdtcp.dataBytesList[1], "little")
        self.image : np.ndarray = np.ndarray(shape=(self.rows, self.cols, 3), buffer=dcdtcp.dataBytesList[2], dtype=np.uint8)
        self.time : str = dcdtcp.dataBytesList[3].decode()

class DcdLogin(DcdImage):
    def __init__(self, dcdtcp : DecodeTCP):
        super().__init__(dcdtcp)

class DcdDrivingImage(DcdImage):
    def __init__(self, dcdtcp : DecodeTCP):
        super().__init__(dcdtcp)

class DcdDrowsyCount:
    def __init__(self, dcdtcp : DecodeTCP):
        self.count : int = int.from_bytes(dcdtcp.dataBytesList[0], "little")
        

# class DcdImage:
#     def __init__(self, dcdtcp : DecodeTCP):
#         self.rows : int = int.from_bytes(dcdtcp.dataBytesList[0], "little")
#         self.cols : int = int.from_bytes(dcdtcp.dataBytesList[1], "little")
#         self.image : np.ndarray = np.ndarray(shape=(self.rows, self.cols, 3), buffer=dcdtcp.dataBytesList[2], dtype=np.uint8)

# class DcdChat:
#     def __init__(self, dcdtcp : DecodeTCP):
#         self.msg : str = dcdtcp.dataBytesList[0].decode()

# class DcdUDPConnect:
#     def __init__(self, dcdtcp : DecodeTCP):
#         self.servIp : str = dcdtcp.dataBytesList[0].decode()
#         self.port : int = int.from_bytes(dcdtcp.dataBytesList[1], "little")
    
#     def __str__(self):
#         return f"servIp : {self.servIp} / port {self.port}"

class DecodeUDP(Decode):
    def __init__(self, rawData : bytearray):
        super().__init__()
        self.seqNum = -1
        pointer : int = 0

        self.type = int.from_bytes(rawData[pointer : pointer + 4], "little")
        pointer += 4
        self.seqNum = int.from_bytes(rawData[pointer : pointer + 4], "little")
        pointer += 4

        self.dataBytesList.append(rawData[pointer : len(rawData)])

