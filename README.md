# mobile_robot_ros2
ROS2 port of mobile_robot project — 4-wheel skid-steer robot with LiDAR, SLAM, and navigation from ROS Noetic


## Known Limitations
- **RViz2 mesh rendering**: robot meshes do not render visually in RViz2 (TF axes, status, and all data pipelines confirmed correct across multiple launch configurations). Confirmed not a configuration issue — real GPU acceleration is active (Mesa Intel HD Graphics 5500), and the identical mesh files render correctly in Gazebo Sim. Likely a specific RViz2/Jazzy + Intel HD 5500 graphics compatibility issue. Deferred pending further investigation (e.g., checking upstream RViz2 issues for this GPU generation).
