from enum import Enum
import numpy as np

class EncodeType(Enum):
    LoginResult = 0
    DrivingResult = 1

class Encode:
    def __init__(self):
        self.dataBytesList : list[bytearray] = []
        self.headerBytes : bytearray =  bytearray()
        self.dataBytes : bytearray = bytearray()

class EncodeTCP(Encode):
    def __init__(self):
        super().__init__()
    
    def packaging(self, typeValue : int):
        headerList : list[int] = []

        # 헤더
        # 헤더의 길이(4바이트 정수형, 이 길이값은 이 뒤에 오는 데이터의 길이를 의미한다.)
        # + 요청 타입(4바이트 정수형) + 데이터 하나의 바이트 길이(4바이트 정수형) * ((헤더의 길이 / 4바이트) - 1)
        headerList.append(typeValue)
        for db in self.dataBytesList:
            headerList.append(len(db)) # 데이터 하나의 바이트 길이
            self.dataBytes.extend(db) # 
        
        # 헤더의 길이
        self.headerBytes.extend((len(headerList) * 4).to_bytes(4, "little"))
        # 요청 타입 + 데이터 하나의 바이트 길이
        for i in headerList:
            self.headerBytes.extend(i.to_bytes(4, "little"))
    
    def totalSizeByte(self) -> bytes:
        return (len(self.headerBytes) + len(self.dataBytes)).to_bytes(4, "little")

class EcdLoginResult(EncodeTCP):
    def __init__(self, type : int):
        super().__init__()
        self.dataBytesList.append(type.to_bytes(4, "little"))
        self.packaging(EncodeType.LoginResult.value)

class EcdDrivingResult(EncodeTCP):
    def __init__(self, img : np.ndarray):
        super().__init__()
        self.dataBytesList.append(img.shape[0].to_bytes(4, "little"))
        self.dataBytesList.append(img.shape[1].to_bytes(4, "little"))
        self.dataBytesList.append(img.tobytes())
        self.packaging(EncodeType.DrivingResult.value)



        