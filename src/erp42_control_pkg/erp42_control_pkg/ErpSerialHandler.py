#!/usr/bin/env python3

#=====================================================#
# 기능: ERP42 차량의 시리얼 통신 송수신 처리
# - 수신된 시리얼 데이터를 ErpStatusMsg로 디코딩 후 /erp42_status 퍼블리시
# - /erp42_ctrl_cmd 토픽에서 제어 명령을 수신하여 시리얼로 전송
#
# 송신 토픽 (publish):
#   - /erp42_status (msg: ErpStatusMsg)
# 수신 토픽 (subscribe):
#   - /erp42_ctrl_cmd (msg: ErpCmdMsg)
#
# TODO : 작업 완료
# 최종 수정일: 2025.08.02
# 편집자: 김형진, 조재민
#=====================================================#

import rclpy
from rclpy.node import Node
import serial
from erp42_interfaces_pkg.msg import ErpStatusMsg, ErpCmdMsg
from .ByteHandler import ErpMsg2Packet, Packet2ErpMsg


START_BITS = "535458"  # 'STX' in hex

"""
< 송신 데이터 포맷 (ErpCmdMsg -> 시리얼 바이트) >
┌─────┬─────┬─────┬─────┬─────┬──────┬───────┬───────┬────┬─────┬──────┬──────┐
│  S  │  T  │  X  │ A,M │  E  │ Gear │ Speed │ Steer │ Br │ Al  │ ETX0 │ ETX1 │
├─────┼─────┼─────┼─────┼─────┼──────┼───────┼───────┼────┼─────┼──────┼──────┤
│0x53 │0x54 │0x58 │0 , 1│0 , 1│0,1,2 │0 ~ 200│ ±2000 │1~33│0~255│ 0x0D │ 0x0A │
└─────┴─────┴─────┴─────┴─────┴──────┴───────┴───────┴────┴─────┴──────┴──────┘

< 수신 데이터 포맷 (시리얼 바이트 -> ErpStatusMsg) >
┌─────┬─────┬─────┬─────┬─────┬──────┬───────┬───────┬────┬───────┬─────┬──────┬──────┐
│  S  │  T  │  X  │ A,M │  E  │ Gear │ Speed │ Steer │ Br │  ENC  │ Al  │ ETX0 │ ETX1 │
├─────┼─────┼─────┼─────┼─────┼──────┼───────┼───────┼────┼───────┼─────┼──────┼──────┤
│0x53 │0x54 │0x58 │0 , 1│0 , 1│0,1,2 │0 ~ 200│ ±2000 │1~33│ ±2^31 │0~255│ 0x0D │ 0x0A │
└─────┴─────┴─────┴─────┴─────┴──────┴───────┴───────┴────┴───────┴─────┴──────┴──────┘
"""

#====================== 토픽 설정 ======================#
PUB_ERP_STATUS_TOPIC   = "/erp42_status"     # 차량 상태 퍼블리시
SUB_ERP_CMD_TOPIC      = "/erp42_ctrl_cmd"   # 차량 제어 명령 수신


class ERPHandler(Node):
    def __init__(self):
        super().__init__("erp_base_node")

        #------------------ 파라미터 ------------------#
        self.declare_parameter("port", "/dev/ttyUSB0")
        self.declare_parameter("baudrate", 115200)
        port = self.get_parameter("port").get_parameter_value().string_value
        baudrate = self.get_parameter("baudrate").get_parameter_value().integer_value

        self.get_logger().info(f"ERP Serial Port: {port}")
        self.get_logger().info(f"ERP Baudrate  : {baudrate}")

        #------------------ 시리얼 포트 ------------------#
        self.serial = serial.Serial(port=port, baudrate=baudrate)
        self.get_logger().info(f"Serial {port} Connected")

        #------------------ 초기 상태 설정 ------------------#
        self.alive = 0
        self.packet = ErpCmdMsg()
        self.packet.gear = 0
        self.packet.e_stop = False
        self.packet.brake = 1

        #------------------ ROS 2 퍼블리셔/서브스크라이버 ------------------#
        self.status_pub = self.create_publisher(ErpStatusMsg, PUB_ERP_STATUS_TOPIC, 3)
        self.ctrl_sub = self.create_subscription(
            ErpCmdMsg,
            SUB_ERP_CMD_TOPIC,
            self.send_packet_callback,
            3
        )

        #------------------ 주기 타이머 ------------------#
        self.timer = self.create_timer(1.0 / 40.0, self.timer_callback)  # 40Hz loop

    def recvPacket(self):
        try:
            packet = self.serial.read(18)
            hex_data = packet.hex()

            # START_BITS 검사
            if not hex_data.startswith(START_BITS):
                self.get_logger().warn(f"Invalid START_BITS: {hex_data}")
                return

            # 파싱 시도
            try:
                msg = Packet2ErpMsg(packet)
                self.status_pub.publish(msg)
            except Exception as inner_e:
                self.get_logger().warn(f"Packet2ErpMsg Error: {inner_e} | raw: {hex_data}")

        except Exception as e:
            self.get_logger().warn(f"recvPacket Error: {e}")



    # ROS 토픽 콜백: 차량 제어 명령 수신
    def send_packet_callback(self, msg: ErpCmdMsg):
        self.packet = msg

    # 시리얼 전송 처리
    def serial_send(self):
        packet = ErpMsg2Packet(self.packet, self.alive)
        self.serial.write(packet)
        self.alive = (self.alive + 1) % 256

    # 주기 실행 함수
    def timer_callback(self):
        self.recv_packet()
        self.serial_send()



def main(args=None):
    rclpy.init(args=args)
    node = ERPHandler()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down ERPHandler...")
    finally:
        node.serial.close()
        node.destroy_node()
        rclpy.shutdown()
