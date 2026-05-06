#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Bool, String
from cv_bridge import CvBridge
from ultralytics import YOLO
import cv2

class DetectionNode(Node):
    def __init__(self):
        super().__init__('detection_node')

        # Charge le modèle YOLOv8
        self.model = YOLO('yolov8n.pt')
        self.bridge = CvBridge()

        # Abonnement au flux caméra
        self.sub = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        # Publication des alertes
        self.pub_intrusion = self.create_publisher(Bool, '/intrusion_detected', 10)
        self.pub_label = self.create_publisher(String, '/intrusion_label', 10)
        self.pub_image = self.create_publisher(Image, '/camera/detection_image', 10)

        self.get_logger().info('Nœud de détection YOLOv8 démarré !')

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        results = self.model(frame, verbose=False)

        intrusion = False
        labels = []

        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id]
                confidence = float(box.conf[0])

                if class_name == 'person' and confidence > 0.5:
                    intrusion = True
                    labels.append(f'PERSONNE ({confidence:.0%})')
                    self.get_logger().warn(
                        f'INTRUSION DÉTECTÉE : {class_name} ({confidence:.0%})'
                    )

        annotated_frame = results[0].plot()
        self.pub_intrusion.publish(Bool(data=intrusion))

        if labels:
            self.pub_label.publish(String(data=', '.join(labels)))

        annotated_msg = self.bridge.cv2_to_imgmsg(annotated_frame, encoding='bgr8')
        self.pub_image.publish(annotated_msg)

        cv2.imshow('Robot Surveillance - Detection', annotated_frame)
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = DetectionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()