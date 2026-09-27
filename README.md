# Mobile Robot — ROS2 Port (Jazzy / Gazebo Sim)

A ROS2 port of the [ROS1 mobile_robot project](https://github.com/Jivani02/mobile_robot) — the same 4-wheel skid-steer robot, rebuilt on ROS2 Jazzy and Gazebo Sim. Built as a hands-on exercise in migrating a working robotics stack across ROS generations, understanding the real architectural differences rather than just translating syntax.

## Current Status

- Done: **Package structure** — `ament_python` package, built and tested with `colcon`
- Done: **Publisher/Subscriber nodes** — `talker.py` / `listner.py`, using `rclpy`'s class-based node pattern, timers, and entry-point registration
- Done: **Python launch files** — including a launch file that starts multiple nodes together
- Done: **URDF ported and spawning in Gazebo Sim** — robot correctly loads, renders, and simulates physics
- Done: **Differential drive control** — `gz-sim-diff-drive-system` plugin, bridged to ROS2 via `ros_gz_bridge`, confirmed driving via `/cmd_vel`
- Done: **LiDAR sensing** — `gpu_lidar` sensor, bridged to `/scan`, confirmed producing real range data against walls/obstacles
- Done: **SLAM** — `slam_toolbox`, confirmed publishing a real, populated `/map` (occupancy grid) while driving

**Known limitation:**
- **RViz2 mesh rendering** — robot meshes do not render visually in RViz2, despite correct TF, `robot_description`, and display status (confirmed across multiple launch configurations). Confirmed not a configuration issue: identical meshes render correctly in Gazebo Sim, and real GPU acceleration is active (Mesa Intel HD Graphics 5500). Likely a specific RViz2/Jazzy + Intel HD 5500 graphics compatibility issue. TF, Map, and LaserScan displays all render correctly, so this does not block SLAM/navigation monitoring.

**Planned next:**
- Nav2 (autonomous navigation)
- Stereo camera port
- Independent 4-wheel drive

## Tech Stack

- **ROS2 (Jazzy)**
- **Gazebo Sim** (formerly Ignition Gazebo)
- **rclpy**, **colcon**
- **slam_toolbox**, **ros_gz_bridge**

## Repository Structure

```
mobile_robot_ros2/
├── mobile_robot/
│ ├── mobile_robot/ # Python node source (talker.py, listner.py)
│ ├── launch/ # Launch files (talk/listen, display, Gazebo Sim, SLAM)
│ ├── urdf/ # Robot description
│ ├── meshes/ # STL mesh files
│ ├── config/ # SLAM parameters
│ ├── package.xml
│ └── setup.py
└── README.md
```


## Running the Simulation

```bash
# Build the workspace
cd ~/ros2_ws
colcon build
source install/setup.bash

# Spawn the robot in Gazebo Sim
ros2 launch mobile_robot gazebo.launch.py

# Drive it manually
ros2 run teleop_twist_keyboard teleop_twist_keyboard

# Build a map with SLAM (run alongside gazebo.launch.py)
ros2 launch mobile_robot slam.launch.py

# View the robot model and TF frames only (no simulation)
ros2 launch mobile_robot display.launch.py
```

## Key Engineering Challenges Solved

- **Mesh resource resolution**: Gazebo Sim's `model://` URI resolution failed to locate mesh files despite correct package structure, causing rendering errors in both Gazebo Sim and RViz2. Fixed by adding the package's share directory to `GZ_SIM_RESOURCE_PATH`.
- **Duplicate sensor-system plugin crash**: Loading the robot alongside any world file beyond Gazebo's built-in empty world caused a hard `Ogre::ItemIdentityException` crash. Root cause: both the world file and the robot's own URDF declared the `gz-sim-sensors-system` plugin, causing Gazebo's rendering engine to attempt duplicate scene/material initialization. Removing the redundant URDF-level plugin declaration (letting the world provide it once) resolved the crash.
- **Missing TF broadcast from odometry**: The `DiffDrive` plugin computed odometry internally but never published it as a TF transform, since Gazebo Sim requires explicit `odom_topic`/`frame_id`/`child_frame_id`/`tf_topic` parameters (unlike Gazebo Classic's simpler `broadcastTF` flag). Diagnosed by checking Gazebo's internal topics directly (`gz topic -l`) and comparing against ROS2's TF tree.
- **Gazebo-to-ROS2 bridge gaps**: Odometry and joint-state data existed inside Gazebo's internal transport system but were never reaching ROS2, since `ros_gz_bridge` requires each topic to be explicitly bridged with a matching ROS2/Gazebo message-type pair. Diagnosed by checking `gz topic -l` against `ros2 topic list` directly.
- **URDF-to-SDF fixed-joint lumping**: Gazebo Sim's URDF-to-SDF conversion merges links connected by fixed joints into their parent by default, which silently absorbed the LiDAR link into the robot's root link, corrupting the sensor's published frame name and breaking SLAM's TF lookups. Fixed by adding `preserveFixedJoint` to the relevant joint, plus a `static_transform_publisher` bridging Gazebo's auto-generated hierarchical frame name to the robot's actual URDF frame name.
- **Systematic root-cause tracing**: A `/map` topic that existed but never published data was traced through a complete diagnostic chain — verifying scan data, TF chain completeness, node lifecycle state, subscriber connections, and finally the params-file installation path — rather than guessing, isolating four independent, real bugs one at a time.

## Roadmap

Core navigation stack (drive, sensing, SLAM) ported and confirmed working. Nav2 and remaining sensor ports planned next. See commit history for detailed progress.
