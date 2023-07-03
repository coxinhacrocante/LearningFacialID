import cv2
import mediapipe as mp
import time
import handtraking_module as htm
import math
import numpy as np

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

def cal_dist(tupla1, tupla2):
    x1, y1 = tupla1[0], tupla1[1]
    x2, y2 = tupla2[0], tupla2[1]
    length = math.hypot(math.fabs(x2 - x1), math.fabs(y2 - y1))
    return length


wCam, hCam = 300, 240       #Definindo a largura e a altura da imagem da câmera

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
cap.set(cv2.CAP_PROP_EXPOSURE, -2.0)

pTime = 0

detector = htm.HandDetector(detectionCon = 0.7)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
volume.SetMasterVolumeLevel(-10.0, None)

vol = 0
volBar = 400
volPer = 0 

while True:
    success, img = cap.read()

    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    
    if len(lmList) != 0:

        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1+x2) // 2 , (y1 + y2) // 2

        length = math.hypot(math.fabs(x2 - x1), math.fabs(y2 - y1))

        cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)    #Círculo no dedão
        cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)    #Círculo no indicador
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 2)         #Linha entre indicador e dedão

        if length > 50:
            cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED) #Círculo rosa
        else:
            cv2.circle(img, (cx, cy), 5, (0, 255, 0), cv2.FILLED)   #Círculo verde

        volBar = np.interp(length, [20,200], [400, 150])
        volPer = np.interp(length, [20,200], [0,100])
        vol = np.interp(length, [20, 200], [minVol, maxVol])
        print(int(length), vol)
        volume.SetMasterVolumeLevel(vol, None) 

    cv2.rectangle(img, (20, 200), (85, 400), (0, 255, 0), 3)
    cv2.rectangle(img, (20, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)}%', (20, 120), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2)     #Plotando o FPS


    cTime = time.time()         #Medindo o fps do vídeo
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (10, 20), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0), 2)     #Plotando o FPS

    cv2.imshow('img', img)
    cv2.waitKey(1)
