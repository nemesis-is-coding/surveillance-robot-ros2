#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry

class FrameFix(Node):
    def __init__(self):
        super().__init__('frame_fix')
        self.sub = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10)
        self.pub = self.create_publisher(
            Odometry, '/odom_fixed', 10)
        self.get_logger().info('Frame fix démarré !')

    def odom_callback(self, msg):
        msg.header.frame_id = 'odom'
        msg.child_frame_id = 'base_link'
        self.pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = FrameFix()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()