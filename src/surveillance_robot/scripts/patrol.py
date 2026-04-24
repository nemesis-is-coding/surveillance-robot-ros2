#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
import math

class PatrolNode(Node):
    def __init__(self):
        super().__init__('patrol_node')
        self._client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        # Waypoints de patrouille (x, y, angle en degrés)
        self.waypoints = [
            (3.0,  3.0,  0.0),
            (3.0, -3.0, -90.0),
            (-3.0, -3.0, 180.0),
            (-3.0,  3.0,  90.0),
        ]
        self.current_waypoint = 0
        self.get_logger().info('Nœud de patrouille démarré !')

    def send_next_waypoint(self):
        x, y, angle_deg = self.waypoints[self.current_waypoint]
        self.get_logger().info(
            f'Navigation vers waypoint {self.current_waypoint}: ({x}, {y})'
        )

        goal = NavigateToPose.Goal()
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.position.z = 0.0

        # Convertit l'angle en quaternion
        angle_rad = math.radians(angle_deg)
        pose.pose.orientation.z = math.sin(angle_rad / 2)
        pose.pose.orientation.w = math.cos(angle_rad / 2)

        goal.pose = pose

        self._client.wait_for_server()
        future = self._client.send_goal_async(
            goal,
            feedback_callback=self.feedback_callback
        )
        future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warn('Waypoint refusé !')
            return
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    def result_callback(self, future):
        self.get_logger().info(
            f'Waypoint {self.current_waypoint} atteint !'
        )
        # Passe au waypoint suivant en boucle
        self.current_waypoint = (self.current_waypoint + 1) % len(self.waypoints)
        self.send_next_waypoint()

    def feedback_callback(self, feedback):
        dist = feedback.feedback.distance_remaining
        self.get_logger().info(f'Distance restante : {dist:.2f} m', throttle_duration_sec=2.0)

def main(args=None):
    rclpy.init(args=args)
    node = PatrolNode()

    # Attend que Nav2 soit prêt puis démarre
    import time
    time.sleep(3.0)
    node.send_next_waypoint()

    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()