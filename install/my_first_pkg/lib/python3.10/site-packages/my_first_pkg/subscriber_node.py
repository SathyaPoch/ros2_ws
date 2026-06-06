import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class SubscriberNode(Node):
    def __init__(self):
        # call super() in the constructor to initialize the Node object
        # the parameter we pass is the node name
        super().__init__('subscriber_node')
        # create a subscription to caro/message topic
        self.subscription = self.create_subscription(
            String,
            'caro/message',
            self.listener_callback,
            10)
        
    def listener_callback(self, msg):
        # callback function that receives messages from caro_node
        self.get_logger().info(f"I heard: {msg.data}")

def main(args=None):
    # initialize the ROS2 communication
    rclpy.init(args=args)
    # declare the node constructor
    node = SubscriberNode()
    # keeps the node alive, waits for a request to kill the node (ctrl+c)
    rclpy.spin(node)
    # shutdown the ROS2 communication
    rclpy.shutdown()

if __name__ == '__main__':
    main()
