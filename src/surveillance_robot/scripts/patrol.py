#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time

class PatrolNode(Node):
    def __init__(self):
        super().__init__('patrol_node')
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.get_logger().info('Patrouille démarrée !')
        self.timer = self.create_timer(0.1, self.patrol_loop)

        # Séquence lente avec petits déplacements
        self.sequence = [
            (0.15, 0.0,  3.0),   # Avance lentement
            (0.0,  0.5,  3.14),  # Tourne 90° lentement
            (0.15, 0.0,  3.0),   # Avance
            (0.0,  0.5,  3.14),  # Tourne 90°
            (0.15, 0.0,  3.0),   # Avance
            (0.0,  0.5,  3.14),  # Tourne 90°
            (0.15, 0.0,  3.0),   # Avance
            (0.0,  0.5,  3.14),  # Tourne 90°
        ]

        self.step = 0
        self.step_start = time.time()

    def patrol_loop(self):
        now = time.time()
        linear, angular, duration = self.sequence[self.step]

        if now - self.step_start > duration:
            # Stop entre chaque étape
            stop = Twist()
            self.pub.publish(stop)
            time.sleep(0.5)

            self.step = (self.step + 1) % len(self.sequence)