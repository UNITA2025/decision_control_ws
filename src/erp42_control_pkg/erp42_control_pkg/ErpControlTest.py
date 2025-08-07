#!/usr/bin/env python3
"""
Steering Test Node for ERP42 ROS2 Control
- Publishes ErpCmdMsg on /erp_cmd to perform a left/right steering-only test:
  Alternates steer between left and right for a fixed number of cycles, then triggers e_stop.
"""

import rclpy
from rclpy.node import Node
from erp42_interfaces_pkg.msg import ErpCmdMsg

class SteeringTestNode(Node):
    def __init__(self):
        super().__init__('steering_test_node')
        self.publisher = self.create_publisher(ErpCmdMsg, '/erp42_ctrl_cmd', 10)
        self.timer_period = 1.0  # 1초마다 실행
        self.timer = self.create_timer(self.timer_period, self.publish_steer_command)
        self.step = 0
        self.cycles = 10         # 좌우 전환 횟수

    def publish_steer_command(self):
        msg = ErpCmdMsg()
        if self.step < self.cycles:
            msg.e_stop = False
            msg.gear    = 1        # 전진 기어 고정
            msg.speed   = 0      # 속도 고정
            # 짝수 스텝엔 좌회전, 홀수 스텝엔 우회전
            msg.steer   = -2000 if self.step % 2 == 0 else 2000
            msg.brake   = 0
        else:
            msg.e_stop = True      # 테스트 종료 시 비상정지

        self.publisher.publish(msg)
        self.get_logger().info(
            f'[Step {self.step}] steer={msg.steer}, e_stop={msg.e_stop}'
        )
        self.step += 1

        # 모든 사이클 완료 후 노드 종료
        if self.step > self.cycles + 2:
            rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    node = SteeringTestNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
