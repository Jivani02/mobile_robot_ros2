import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node

# Path to your URDF
urdf_path = os.path.join(
    get_package_share_directory('mobile_robot'),
    'urdf',
    'mobile_robot.urdf'
)

# Path to Gazebo Sim's own launch file
gz_launch_path = os.path.join(
    get_package_share_directory('ros_gz_sim'),
    'launch',
    'gz_sim.launch.py'
)


def generate_launch_description():
    return LaunchDescription([

        # Start Gazebo Sim itself, with an empty world
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(gz_launch_path),
            launch_arguments={'gz_args': '-r empty.sdf'}.items()
        ),

        # Publish robot_description and TF, same as your RViz2 launch file
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            parameters=[{'robot_description': Command(['xacro ', urdf_path])}]
        ),

        # Spawn the robot into Gazebo Sim, reading from the /robot_description topic
        Node(
            package='ros_gz_sim',
            executable='create',
            arguments=[
                '-topic', 'robot_description',
                '-name', 'mobile_robot',
                '-z', '0.5'
            ],
            output='screen'
        ),
            
        # Cmd_vel bridge from gazebo to ros2
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
                '/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan'
            ],
            output='screen'
        ),
    ])