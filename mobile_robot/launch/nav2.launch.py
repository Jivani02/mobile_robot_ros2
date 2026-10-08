import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

nav2_launch_path = os.path.join(
    get_package_share_directory('nav2_bringup'),
    'launch',
    'bringup_launch.py'
)

nav2_params_path = os.path.join(
    get_package_share_directory('mobile_robot'),
    'config',
    'nav2_params.yaml'
)

map_path = os.path.join(
    get_package_share_directory('mobile_robot'),
    'maps',
    'house_map.yaml'
)


def generate_launch_description():
    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(nav2_launch_path),
            launch_arguments={
                'params_file':nav2_params_path,
                'map':map_path,
                'use_sim_time': 'true'
            }.items(),
        )
    ])