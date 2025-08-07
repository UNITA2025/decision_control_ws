#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from erp42_interfaces_pkg.msg import ErpCmdMsg

class MotorOnlyParkingTestNode(Node):
    # parallel parking states
    APPROACH = 'APPROACH'
    ENTRY    = 'ENTRY'
    ADJUST   = 'ADJUST'
    STRAIGHT = 'STRAIGHT'
    DONE     = 'DONE'

    def __init__(self):
        super().__init__('motor_only_parking_test_node')
        self.publisher = self.create_publisher(ErpCmdMsg, '/erp42_ctrl_cmd', 10)

        # --- timing parameters (seconds) ---
        self.forward_duration  = 3.0   # 전진 시간
        self.entry_duration    = 2.0   # 후진+우회전 시간
        self.adjust_duration   = 2.0   # 후진+좌회전 시간
        self.straight_duration = 1.0   # 후진+직진 정렬 시간

        # --- motion parameters ---
        self.forward_speed = 30       # 0~200
        self.reverse_speed = 30       # 0~200
        self.steer_right   = -1000     # −2000~+2000 (우회전)
        self.steer_left    = +1000     # −2000~+2000 (좌회전)
        self.steer_straight = 0

        # initialize state machine
        self.state = self.APPROACH
        self.state_start_time = self.get_clock().now().to_sec()

        # run at 10 Hz
        self.timer = self.create_timer(0.1, self.timer_callback)

    def timer_callback(self):
        now = self.get_clock().now().to_sec()
        elapsed = now - self.state_start_time

        msg = ErpCmdMsg()
        msg.e_stop = False
        msg.brake  = 1

        if self.state == self.APPROACH:
            # 1) 직진
            if elapsed < self.forward_duration:
                msg.gear  = 0
                msg.speed = self.forward_speed
                msg.steer = self.steer_straight
            else:
                self.transition_to(self.ENTRY)
                return

        elif self.state == self.ENTRY:
            # 2) 후진하며 우회전
            if elapsed < self.entry_duration:
                msg.gear  = 2
                msg.speed = self.reverse_speed
                msg.steer = self.steer_right
            else:
                self.transition_to(self.ADJUST)
                return

        elif self.state == self.ADJUST:
            # 3) 후진하며 좌회전
            if elapsed < self.adjust_duration:
                msg.gear  = 2
                msg.speed = self.reverse_speed
                msg.steer = self.steer_left
            else:
                self.transition_to(self.STRAIGHT)
                return

        elif self.state == self.STRAIGHT:
            # 4) 후진하며 직진 정렬
            if elapsed < self.straight_duration:
                msg.gear  = 2
                msg.speed = self.reverse_speed
                msg.steer = self.steer_straight
            else:
                self.transition_to(self.DONE)
                return

        elif self.state == self.DONE:
            # 5) 정지
            msg.gear  = 0
            msg.speed = 0
            msg.steer = self.steer_straight

        # publish the command for all states except immediate transitions
        self.publisher.publish(msg)

    def transition_to(self, new_state: str):
        self.get_logger().info(f'Transition: {self.state} → {new_state}')
        self.state = new_state
        self.state_start_time = self.get_clock().now().to_sec()


def main(args=None):
    rclpy.init(args=args)
    node = MotorOnlyParkingTestNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down MotorOnlyParkingTestNode...")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
