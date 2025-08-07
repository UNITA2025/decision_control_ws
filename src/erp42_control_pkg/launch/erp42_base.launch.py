#!/usr/bin/env python3

#=====================================================#
# 기능: ErpSerialHandler 노드의 래핑을 위한 런치파일.
# - 필요시 포트 및 보레이트 설정 가능
# - 실행 후 노드 이름은 'erp_base_node'로 설정됨
#
# TODO : 작업 완료
# 최종 수정일: 2025.08.02
# 편집자: 김형진
#=====================================================#

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='erp42_control_pkg',
            executable='ErpSerialHandler_node',
            name='erp_base_node',
            output='screen',
            parameters=[
                {"port": "/dev/ttyUSB0"},       # !
                {"baudrate": 115200}            # !
            ]
        )
    ])
