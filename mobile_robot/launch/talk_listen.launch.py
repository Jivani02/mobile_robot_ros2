from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='mobile_robot',
            executable='talker',
            name='talker_node'
        ),
        Node(
            package='mobile_robot',
            executable='listner',
            name='listner_node'
        ),
    ])