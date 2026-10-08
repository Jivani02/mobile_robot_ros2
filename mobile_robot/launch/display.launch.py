import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command
from launch_ros.descriptions import ParameterValue


def generate_launch_description():
    # 1. Locate the plain .urdf file
    urdf_path = os.path.join(
        get_package_share_directory('mobile_robot'),
        'urdf',
        'mobile_robot.urdf'
    )
    
    robot_description_content = ParameterValue(
        Command(['cat ', urdf_path]), 
        value_type=str
    )
    
    

    return LaunchDescription([
        # Robot State Publisher Node
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': robot_description_content,
                'use_sim_time': True
            }],
        ),
        
        # RViz2 Node
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            parameters=[{
                'use_sim_time': True
            }],
        ),
    ])
