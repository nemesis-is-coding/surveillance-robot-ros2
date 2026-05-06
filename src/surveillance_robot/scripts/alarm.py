#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, String
import subprocess
import time

class AlarmNode(Node):
    def __init__(self):
        super().__init__('alarm_node')

        self.sub_intrusion = self.create_subscription(
            Bool,
            '/intrusion_detected',
            self.intrusion_callback,
            10
        )

        self.sub_label = self.create_subscription(
            String,
            '/intrusion_label',
            self.label_callback,
            10
        )

        self.alarm_active = False
        self.last_alarm_time = 0
        self.cooldown = 5.0  # secondes entre chaque alarme

        self.get_logger().info('Nœud alarme démarré — surveillance active !')

    def label_callback(self, msg):
        self.get_logger().warn(f'Objet détecté : {msg.data}')

    def intrusion_callback(self, msg):
        if msg.data:
            now = time.time()
            if now - self.last_alarm_time > self.cooldown:
                self.last_alarm_time = now
                self.trigger_alarm()
        else:
            if self.alarm_active:
                self.alarm_active = False
                self.get_logger().info('Zone sécurisée — alarme désactivée')

    def trigger_alarm(self):
        self.alarm_active = True
        self.get_logger().warn('🚨 ALARME DÉCLENCHÉE — INTRUSION DÉTECTÉE !')

        # Alarme sonore via terminal (fonctionne sur WSL)
        try:
            subprocess.Popen(['bash', '-c', 'echo -e "\\a\\a\\a"'])
        except Exception:
            pass

        # Affiche une alerte visuelle dans le terminal
        print('\n' + '='*50)
        print('🚨  ALERTE SÉCURITÉ  🚨')
        print('INTRUSION DÉTECTÉE PAR LE ROBOT DE SURVEILLANCE')
        print(f'Heure : {time.strftime("%H:%M:%S")}')
        print('='*50 + '\n')

def main(args=None):
    rclpy.init(args=args)
    node = AlarmNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()