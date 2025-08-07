#! /usr/bin/env python3

#=====================================================#
# 기능:
# - ERP-42 차량의 시리얼 데이터 ↔ ROS 2 메시지 변환 처리
# - 수신된 바이트 데이터를 erpStatusMsg로 변환 (Packet2ErpMsg)
# - ROS 2 erpCmdMsg를 전송용 바이트 패킷으로 변환 (ErpMsg2Packet)
# - ErpSerialHandler.py에서 사용됨
#
# TODO : 작업 완료
#
# 최종 수정일: 2025.08.02
# 편집자: 김형진, 조재민
#=====================================================#

import struct
import numpy as np
from erp42_interfaces_pkg.msg import ErpStatusMsg, ErpCmdMsg


def Packet2ErpMsg(_byte: bytes) -> ErpStatusMsg:
    formated_packet = struct.unpack('<BBBBBBhhBiBBB', _byte)
    msg = ErpStatusMsg()
    msg.control_mode = formated_packet[3]
    msg.e_stop = bool(formated_packet[4])
    msg.gear = formated_packet[5]
    msg.speed = formated_packet[6]
    msg.steer = -formated_packet[7]
    msg.brake = formated_packet[8]
    msg.encoder = int(formated_packet[9])
    msg.alive = formated_packet[10]
    return msg


def ErpMsg2Packet(_msg: ErpCmdMsg, _alive: np.uint8) -> list:
    header = "STX".encode()
    tail="\r\n".encode()

    data = struct.pack(
        ">BBBHhBB", 1,
        _msg.e_stop,
        _msg.gear,
        _msg.speed,
        _msg.steer,
        _msg.brake,
        _alive
    )
    packet = header + data + tail
    return packet