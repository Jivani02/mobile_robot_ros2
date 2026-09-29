import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

# slam launch file path
slam_launch_path = os.path.join(
    get_package_share_directory('slam_toolbox'),
    'launch',
    'online_async_launch.py'
    )

# editied yaml file path
slam_params_path = os.path.join(
    get_package_share_directory('mobile_robot'),
    'config',
    'mapper_params.yaml'
)


def generate_launch_description():
    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(slam_launch_path),
            launch_arguments = {'slam_params_file':slam_params_path,
                                'use_sim_time': 'true' 
            }.items(),
                        
        )
    ])