import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
import math

class HouseNavigator(Node):
    def __init__(self):
        super().__init__('house_navigator')
        
        # 1. Create Publisher to move the robot
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # 2. Create Subscriber to read odometry
        self.subscription = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)

        # State Machine Variables
        self.state = 0
        self.cmd = Twist()
        
        # Variables to track where we started our current movement
        self.initial_pose_saved = False
        self.start_x = 0.0
        self.start_y = 0.0
        self.start_yaw = 0.0

        # --- TUNING PARAMETERS ---
        # You will need to change these values based on your specific Gazebo world size!
        self.distance_to_door = 2.9    # D1: Distance to move forward until parallel to door
        self.turn_left_angle = math.pi/2 # 90 degrees in radians (positive is left)
        self.distance_through_door = 0.8# D2: Distance to drive through the wall opening
        self.turn_right_angle = -math.pi/2 # -90 degrees in radians (negative is right)
        self.distance_to_stop = 3     # D3: Final distance to drive into the stop area
        # -------------------------

    # Helper function: Odometry gives orientation in Quaternions (x, y, z, w). 
    # This converts it to Euler Yaw (Z-axis rotation in radians) which is easier to work with.
    def get_yaw_from_quaternion(self, q):
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        return math.atan2(siny_cosp, cosy_cosp)

    def odom_callback(self, msg: Odometry):
        # Extract current position and yaw
        current_x = msg.pose.pose.position.x
        current_y = msg.pose.pose.position.y
        current_yaw = self.get_yaw_from_quaternion(msg.pose.pose.orientation)

        # Save the starting position the very first time we enter a new state
        if not self.initial_pose_saved:
            self.start_x = current_x
            self.start_y = current_y
            self.start_yaw = current_yaw
            self.initial_pose_saved = True
            return

        # Calculate how far we've moved/turned since the state began
        distance_moved = math.sqrt((current_x - self.start_x)**2 + (current_y - self.start_y)**2)
        angle_turned = current_yaw - self.start_yaw
        
        # Normalize angle to be between -pi and pi
        angle_turned = math.atan2(math.sin(angle_turned), math.cos(angle_turned))

        # --- STATE MACHINE LOGIC ---
        if self.state == 0:
            # 1. Move forward until parallel with opening
            if distance_moved < self.distance_to_door:
                self.cmd.linear.x = 0.8  # Move forward at 0.2 m/s
                self.cmd.angular.z = 0.0
            else:
                self.transition_state()

        elif self.state == 1:
            # 2. Rotate 90 degrees left (direction of opening)
            if abs(angle_turned) < abs(self.turn_left_angle):
                self.cmd.linear.x = 0.0
                self.cmd.angular.z = 0.8 # Rotate left at 0.2 rad/s
            else:
                self.transition_state()

        elif self.state == 2:
            # 3. Move forward past the opening
            if distance_moved < self.distance_through_door:
                self.cmd.linear.x = 0.2
                self.cmd.angular.z = 0.0
            else:
                self.transition_state()

        elif self.state == 3:
            # 4. Turn right to face the second door
            if abs(angle_turned) < abs(self.turn_right_angle):
                self.cmd.linear.x = 0.0
                self.cmd.angular.z = -0.2 # Rotate right at -0.2 rad/s
            else:
                self.transition_state()

        elif self.state == 4:
            # 5. Go inside the door
            if distance_moved < self.distance_to_stop:
                self.cmd.linear.x = 0.8
                self.cmd.angular.z = 0.0
            else:
                self.transition_state()

        elif self.state == 5:
            # 6. Stop
            self.cmd.linear.x = 0.0
            self.cmd.angular.z = 0.0
            self.get_logger().info('Robot has reached the stop area!', once=True)
        

        # Publish the command based on the current state
        self.publisher_.publish(self.cmd)

    def transition_state(self):
        # Stop the robot momentarily, reset the start pose, and increment state
        self.cmd.linear.x = 0.0
        self.cmd.angular.z = 0.0
        self.publisher_.publish(self.cmd)
        
        self.state += 1
        self.initial_pose_saved = False 
        self.get_logger().info(f'Goal reached! Moving to State {self.state}')


def main(args=None):
    rclpy.init(args=args)
    node = HouseNavigator()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Force stop the robot if we hit Ctrl+C
        node.cmd.linear.x = 0.0
        node.cmd.angular.z = 0.0
        node.publisher_.publish(node.cmd)
        
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()