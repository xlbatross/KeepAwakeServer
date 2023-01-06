import socket
from decode import *
from encode import *
from threading import Thread
from mediapipe.python.solutions import face_mesh as fm, drawing_styles as ds, drawing_utils as du
import cv2

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
                if dcdtcp.type == DecodeType.Image.value:
                    dcdtcp = DcdImage(dcdtcp)

                    image = cv2.cvtColor(dcdtcp.image, cv2.COLOR_BGR2RGB)

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

                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                    ecdtcp = EcdImage(image)

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