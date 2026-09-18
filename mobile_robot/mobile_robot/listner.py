import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class listner(Node):
    def __init__(self):
        super().__init__('listner_node')
        self.sub = self.create_subscription(String, '/chatter',self.callback,10)


    def callback(self,msg):
        self.get_logger().info(msg.data)

def main(args=None):
    rclpy.init(args=args)
    node = listner()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

