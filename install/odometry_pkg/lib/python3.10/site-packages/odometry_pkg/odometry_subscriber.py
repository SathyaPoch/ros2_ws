import rclpy
from rclpy.node import Node

from nav_msgs.msg import Odometry


class OdomSubscriber(Node):

    def __init__(self):
        super().__init__('odometry_subscriber')

        # Create subscription
        self.subscription = self.create_subscription(
            Odometry,
            '/odom',   # topic name
            self.odom_callback,
            10
        )

    def odom_callback(self, msg: Odometry):
        # Position
        position = msg.pose.pose.position
        # Orientation
        orientation = msg.pose.pose.orientation
        # Linear velocity
        linear = msg.twist.twist.linear
        # Angular velocity
        angular = msg.twist.twist.angular

        self.get_logger().info(
            f"\nPosition: x={position.x:.2f}, y={position.y:.2f}, z={position.z:.2f}\n"
            f"Orientation: x={orientation.x:.2f}, y={orientation.y:.2f}, "
            f"z={orientation.z:.2f}, w={orientation.w:.2f}\n"
            f"Linear Velocity: x={linear.x:.2f}, y={linear.y:.2f}, z={linear.z:.2f}\n"
            f"Angular Velocity: x={angular.x:.2f}, y={angular.y:.2f}, z={angular.z:.2f}\n"
        )


def main(args=None):
    rclpy.init(args=args)

    node = OdomSubscriber()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()