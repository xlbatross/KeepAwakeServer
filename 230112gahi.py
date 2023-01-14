import socket
from decode import *
from encode import *
from threading import Thread
from mediapipe.python.solutions import face_mesh as fm, drawing_styles as ds, drawing_utils as du
import cv2
import random
import face_recognition
import numpy as np
import os
from DBclass import Database
#가히 import 및 객체 생성
import predictAngle
import predictEye
from datetime import datetime,timedelta

DB = Database()

# #가히 변수 생성
# userID = -1
# closeCount = 0
# alert_text = ""
# drowsyCount = 0
# preDrowsyCount = 0
eyesOpenTime = [] 
eyesCloseTime = []

#userState = True #눈을 뜨고 있으면 True, 눈을 감고 있으면 False

#등록된 사용자의 사진을 불러오고 encoding하는 부분
path = 'pictures'
images = [] #시각화된 이미지가 담긴다 _[[83,105,130],[96,113,132]]이런식으로!
userImgList = [] #[('iu','.jpg')] 이렇게 담김
mylist = os.listdir(path) #폴더 내 이미지 목록을 들고 옴
for cls in mylist:
    currentImg = cv2.imread(f'{path}/{cls}')
    images.append(currentImg)
    userImgList.append(os.path.splitext(cls))

imgsEncodeList = [] #사용자 얼굴 인코딩한 값 담아놓는 리스트 

for img in images:
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) #라이브러리는 RGB로 이해하므로 변환과정 필요
    encode = face_recognition.face_encodings(img)[0] #사진의 모든 좌표값이 나타남
    imgsEncodeList.append(encode)

#시간차구하기
def getDrowsyInterval(count1, count2): #drowsyCount, preDrowsyCount
    print(eyesOpenTime)
    # pre_drowsyCount = drowsyCount -1
    # eyesOpenTime_datetime = list(map(datetime, eyesOpenTime))  #리스트내 모든 원소 한 번에 type바꾸기
    print("drowsyCount : ", count1)
    print("preDrowsyCount : ", count2)
    if count1 == 1:
        time1 = datetime.strptime(eyesOpenTime[count2], '%H:%M:%S') 
        time2 = datetime.strptime(eyesCloseTime[count2], '%H:%M:%S')
    else:
        time1 = datetime.strptime(eyesOpenTime[count2], '%H:%M:%S') 
        time2 = datetime.strptime(eyesOpenTime[count2], '%H:%M:%S')
    time_interval = time1 - time2 #n번째와 n-1번째 졸음 사잇값
    print("시간차 : ", time_interval)
    # result = datetime.strftime(time_interval,'%H:%M:%S')
    result = str(time_interval)
    if len(result) == 7:
        result = '0' + result
    # result = delttime_interval.astype(str)
    print("시간차: ", result)
    print("len : ", len(result))
    print("시간차 type: ",type(result))
    # print(type(time_interval))
    # print("pre_drowsyCount type : ",type(pre_drowsyCount))
    # a = eyesOpenTime[drowsyCount]
    # b = datetime.strptime(a, '%Y/%m/%d %H:%M:%S')
    # print("1번째 : ", eyesOpenTime_datetime[drowsyCount])
    # print("type : ", type(b))
    # time_interval : datetime = datetime(eyesOpenTime[drowsyCount]) - datetime(eyesOpenTime[pre_drowsyCount])
    # return time_interval
    # print("time_interval type : ", type(time_interval))
    return result

print("Encoding completes!")
print(userImgList)

class ClientData:
    def __init__(self):
        self.id : str = ""
        self.noFaceCount : int = 0
        self.eyeBlinkCount : int = 0
        self.otherDirectionCount : int = 0
#   {
#       "id" : "아이디",
#       "noFaceCount" : 얼굴 존재 카운트 = 0, 
#       "eyeBlinkCount" : 눈깜박임 체크 카운트 = 0, 
#       "otherDirectionCount" : 다른 방향 체크 카운트 = 0
#   }

clients : dict[socket.socket, ClientData] = {}

def receiveTCP(sock : socket.socket):
    mp_drawing = du
    mp_drawing_styles = ds
    mp_face_mesh = fm
    #가히 변수 생성
    userID = -1
    closeCount = 0
    alert_text = ""
    drowsyCount = 0
    preDrowsyCount = 0


    with mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as face_mesh:
        while True:
            try:
                # receive byte data
                dataSize : int = int.from_bytes(sock.recv(4), "little")
                recvSize : int = 0
                rawData : bytearray = bytearray()
                while recvSize < dataSize:
                    packetSize = 1024 if recvSize + 1024 < dataSize else dataSize - recvSize
                    packet = sock.recv(packetSize)
                    rawData.extend(packet)
                    recvSize += len(packet)

                # change rawData to decode tcp class
                dcdtcp = DecodeTCP(rawData)

                #
                ecdtcp = None
                
                print(dcdtcp.type)

                # drowsyCount = 0
                # eyesOpenTime = []

                if dcdtcp.type == DecodeType.Login.value:
                    dcdtcp = DcdLogin(dcdtcp)
                    #drowsyCount = 0
                    # eyesOpenTime = []
                    
                    #가히 _ 사용자의 페이스로그인을 시도하는 부분
                    driverImg = cv2.cvtColor(dcdtcp.image, cv2.COLOR_BGR2RGB)
                    driverImgEncodeList = face_recognition.face_encodings(driverImg)
                    #이 프로그램에 등록된 사용자가 한 명도 없을 때
                    if len(imgsEncodeList) == 0: 
                        print("폴더 내 사용자 없음")
                        
                        if len(driverImgEncodeList) == 0:
                            ecdtcp = EcdLoginResult(0)
                        else:
                            driverImgEncode = driverImgEncodeList[0]
                            print("새로운 사용자 등록")
                            imgsEncodeList.append(driverImgEncode)
                            FirstUser = len(imgsEncodeList)
                            userID = FirstUser
                            driverImg = cv2.cvtColor(driverImg, cv2.COLOR_RGB2BGR)
                            driverImgPath = f"./pictures/{FirstUser}.jpg"
                            cv2.imwrite(driverImgPath,driverImg)
                            userImgList.append((f"{FirstUser}",'.jpg'))
                            DB.UserInfoInsert(driverImgPath)
                            ecdtcp = EcdLoginResult(2)
                    #프로그램에 등록된 사용자가 1명 이상일 때
                    else:
                        if len(driverImgEncodeList) == 0:
                            ecdtcp = EcdLoginResult(0)
                        else:
                            driverImgEncode = driverImgEncodeList[0]
                            faces_match = face_recognition.compare_faces(imgsEncodeList, driverImgEncode)
                            faces_faceDis = face_recognition.face_distance(imgsEncodeList, driverImgEncode)
                            matchIndex = np.argmin(faces_faceDis)

                            #로그인 결과 출력
                            # loginSuccess = 1

                            if faces_match[matchIndex] and faces_faceDis[matchIndex] <= 0.4:
                                print("얼굴추측 성공")
                                userIDnum = userImgList[matchIndex][0]
                                driverImgPath = f"./pictures/{userIDnum}.jpg"
                                loginResult = DB.UserLogin(driverImgPath)
                                if loginResult != -1:
                                    userID = loginResult
                                    ecdtcp = EcdLoginResult(1)
                                    drivingStartTime = dcdtcp.time
                                    eyesOpenTime.append(drivingStartTime)
                                    print(eyesOpenTime)
                                else:
                                    ecdtcp = EcdLoginResult(0)
                                drowsyCount = 0
                                preDrowsyCount = 0
                                alert_text = ""
                                eyesOpenTime = []
                                eyesCloseTime = []
                                print("운전자 id:",userID)
                                
                            else:
                                print("등록된 얼굴이 없습니다.")
                                imgsEncodeList.append(driverImgEncode)
                                userNum = len(imgsEncodeList)
                                driverImg = cv2.cvtColor(driverImg, cv2.COLOR_RGB2BGR)
                                driverImgPath = f"./pictures/{userNum}.jpg"
                                cv2.imwrite(driverImgPath,driverImg)
                                userImgList.append((f"{userNum}",'.jpg'))
                                DB.UserInfoInsert(driverImgPath)
                                print("사용자 신규등록 완료")
                                ecdtcp = EcdLoginResult(2)
                    

                elif dcdtcp.type == DecodeType.DrivingImage.value:
                    dcdtcp = DcdDrivingImage(dcdtcp)
                    #userState = True 

                    image = cv2.cvtColor(dcdtcp.image, cv2.COLOR_BGR2RGB)
                    nowTime = dcdtcp.time
                    print("img time : ", nowTime)

                    # To improve performance
                    image.flags.writeable = False
                    # get the result
                    results = face_mesh.process(image)
                    # To improve performance
                    image.flags.writeable = True

                    img_h, img_w, img_c = image.shape

                    if results.multi_face_landmarks:
                        face_landmarks = results.multi_face_landmarks[0]
                        
                        mp_drawing.draw_landmarks(
                            image=image,
                            landmark_list=face_landmarks,
                            connections=mp_face_mesh.FACEMESH_FACE_OVAL,
                            landmark_drawing_spec=None,
                            connection_drawing_spec=mp_drawing.DrawingSpec(color=(245,117,66), thickness=2)
                            # D.get_default_face_mesh_tesselation_style()
                        )
                        

                        eyeData = predictEye.blinkRatio(image, face_landmarks.landmark, predictEye.LEFT_EYE, predictEye.RIGHT_EYE)
                        predictEyeData = predictEye.model.predict([[eyeData]])[0]
                        if predictEyeData == 'close':
                            closeCount += 1

                        else:
                            closeCount = 0

                    if closeCount >= 15 and closeCount % 10 > 1:
                        if preDrowsyCount == drowsyCount:
                            eyesCloseTime.append(nowTime)
                            print("nowTime type : ", type(nowTime))
                            drowsyCount += 1
                            print("함수 전 dc: ", drowsyCount, "함수 전 pdc: ",preDrowsyCount)
                            time_interval = getDrowsyInterval(preDrowsyCount)
                            DB.DrowsyTimeInsert(userID,drowsyCount,time_interval)
                            alert_text = "Detect user's drowsy !"
                            print(alert_text)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
                            
                    elif closeCount == 0 and preDrowsyCount < drowsyCount:
                        preDrowsyCount = drowsyCount
                        eyesOpenTime.append(nowTime)
                        
                    else:
                        alert_text = ""

                    
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                    ecdtcp = EcdDrivingResult(image, alert_text)
                
                #가히
                # elif dcdtcp.type == DecodeType.DrowsyCount.value:
                #     dcdtcp = DcdDrowsyCount(dcdtcp)
                #     drowsyTimes = dcdtcp.count
                   
                #
                if not ecdtcp is None:
                    totalByte = bytearray()
                    totalByte.extend(ecdtcp.totalSizeByte())
                    totalByte.extend(ecdtcp.headerBytes)
                    totalByte.extend(ecdtcp.dataBytes)
                    sock.sendall(totalByte)

            except Exception as e:
                print(e)
                del clients[sock]
                sock.close()
                print(f"{clients}")
                print(f"clients Count : {len(clients)}")
                break

port = 2500
listener = 600

tcpSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # 서버 TCP 소켓 생성
tcpSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # alreay in use 방지용
tcpSock.bind(('', port)) # 서버 소켓에 어드레스(IP가 빈칸일 경우 자기 자신(127.0.0.1)로 인식한다. + 포트번호)를 지정한다.
tcpSock.listen(listener) # 서버 소켓을 연결 요청 대기 상태로 한다.

while True:
    print("waiting for clients...")
    cSock, cAddr = tcpSock.accept() # 클라이언트와 연결이 된다면 클라이언트와 연결된 소켓과 클라이언트의 어드레스(IP와 포트번호)를 반환한다.
    clients[cSock] = ClientData()
    cThread = Thread(target=receiveTCP, args=(cSock, )) # 연결된 클라이언트에 대한 쓰레드 생성
    cThread.daemon = True # 생성된 쓰레드의 데몬 여부를 True로 한다. (데몬 스레드 = 메인 스레드가 종료되면 즉시 종료되는 스레드)
    cThread.start() # 쓰레드 시작
    print(f"clients Count : {len(clients)} / connection {cAddr}")                                    