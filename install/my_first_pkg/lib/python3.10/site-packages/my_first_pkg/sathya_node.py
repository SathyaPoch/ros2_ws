import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class SathyaNode(Node):
    def __init__(self):
        super().__init__('sathya_node')
        
        # Create publisher
        self.publisher_ = self.create_publisher(String, 'caro/message', 10)
        
        # Create timer (publishes every 1 second)
        self.timer = self.create_timer(1.0, self.publish_message)
        
        self.get_logger().info("Publisher node started...")

    def publish_message(self):
        msg = String()
        msg.data = "Hello from Sathya Node !"
        
        self.publisher_.publish(msg)
        self.get_logger().info(f"Publishing: {msg.data}")


def main(args=None):
    rclpy.init(args=args)
    
    node = SathyaNode()
    
    rclpy.spin(node)
    
    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()