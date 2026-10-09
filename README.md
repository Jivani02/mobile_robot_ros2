# Mobile Robot — ROS2 Port (Jazzy / Gazebo Sim)

A ROS2 port of the [ROS1 mobile_robot project](https://github.com/Jivani02/mobile_robot) — the same 4-wheel skid-steer robot, rebuilt on ROS2 Jazzy and Gazebo Sim. Built as a hands-on exercise in migrating a working robotics stack across ROS generations, understanding the real architectural differences rather than just translating syntax.

## Current Status

- Done: **Package structure** — `ament_python` package, built and tested with `colcon`
- Done: **Publisher/Subscriber nodes** — `talker.py` / `listner.py`, using `rclpy`'s class-based node pattern, timers, and entry-point registration
- Done: **Python launch files** — including a launch file that starts multiple nodes together
- Done: **URDF ported and spawning in Gazebo Sim** — robot correctly loads, renders, and simulates physics
- Done: **Differential drive control** — `gz-sim-diff-drive-system` plugin, bridged to ROS2 via `ros_gz_bridge`, confirmed driving via `/cmd_vel`
- Done: **LiDAR sensing** — `gpu_lidar` sensor, bridged to `/scan`, confirmed producing real range data against walls/obstacles
- Done: **SLAM** — slam_toolbox, saved a clean occupancy-grid map of the house world (maps/house_map.yaml)
- Done: **Odometry calibration** — wheel_separation tuned empirically from controlled rotation tests (angular odometry error ~50% → ~1%)
- Done: **Robot model in RViz2** — meshes render alongside TF, map and LaserScan displays
- Done: **Nav2 localization & planning** — nav2_bringup with AMCL on the saved map; global path planning, costmaps and goal execution verified end-to-end in simulation, including routing through a narrow doorway; RViz2 pose and Gazebo pose aligned (same position and heading)

## In progress:

- add Stereo camera

## Tech Stack

- **ROS2 (Jazzy)**
- **Gazebo Sim** (formerly Ignition Gazebo)
- **rclpy**, **colcon**
- **slam_toolbox**, **Nav2 (AMCL, map_server, planner/controller servers, behavior tree navigator)**,**ros_gz_bridge**

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


# Navigate autonomously on the saved map (run alongside gazebo.launch.py)
ros2 launch mobile_robot nav2.launch.py
# In RViz2: set the 2D Goal Pose

# View the robot model and TF frames only (no simulation)
ros2 launch mobile_robot display.launch.py
```

## RViz2 Setup (robot model, map, scan)
- Global Options → Fixed Frame: map (use odom if no map/AMCL is running yet)
- RobotModel: Description Source = Topic, Description Topic = /robot_description, Durability Policy = Transient Local (the description is published once, so a volatile subscription misses it)
- TF: enable to check map → odom → dummy_root → body1 → wheels / lidar_link
- Map: Topic = /map, Durability Policy = Transient Local, Reliability = Reliable (the map server latches the map; a volatile display shows "No map received")
- LaserScan: Topic = /scan, Fixed Frame map
- Nav2: set the pose with 2D Pose Estimate (or use the initial_pose in nav2_params.yaml), then 2D Goal Pose

## Key Engineering Challenges Solved

- **Mesh resource resolution**: Gazebo Sim's `model://` URI resolution failed to locate mesh files despite correct package structure, causing rendering errors in both Gazebo Sim and RViz2. Fixed by adding the package's share directory to `GZ_SIM_RESOURCE_PATH`.
- **Duplicate sensor-system plugin crash**: Loading the robot alongside any world file beyond Gazebo's built-in empty world caused a hard `Ogre::ItemIdentityException` crash. Root cause: both the world file and the robot's own URDF declared the `gz-sim-sensors-system` plugin, causing Gazebo's rendering engine to attempt duplicate scene/material initialization. Removing the redundant URDF-level plugin declaration (letting the world provide it once) resolved the crash.
- **Missing TF broadcast from odometry**: The `DiffDrive` plugin computed odometry internally but never published it as a TF transform, since Gazebo Sim requires explicit `odom_topic`/`frame_id`/`child_frame_id`/`tf_topic` parameters (unlike Gazebo Classic's simpler `broadcastTF` flag). Diagnosed by checking Gazebo's internal topics directly (`gz topic -l`) and comparing against ROS2's TF tree.
- **Gazebo-to-ROS2 bridge gaps**: Odometry and joint-state data existed inside Gazebo's internal transport system but were never reaching ROS2, since `ros_gz_bridge` requires each topic to be explicitly bridged with a matching ROS2/Gazebo message-type pair. Diagnosed by checking `gz topic -l` against `ros2 topic list` directly.
- **URDF-to-SDF fixed-joint lumping**: Gazebo Sim's URDF-to-SDF conversion merges links connected by fixed joints into their parent by default, which silently absorbed the LiDAR link into the robot's root link, corrupting the sensor's published frame name and breaking SLAM's TF lookups. Fixed by adding `preserveFixedJoint` to the relevant joint, plus a `static_transform_publisher` bridging Gazebo's auto-generated hierarchical frame name to the robot's actual URDF frame name.
- **Systematic root-cause tracing**: A `/map` topic that existed but never published data was traced through a complete diagnostic chain — verifying scan data, TF chain completeness, node lifecycle state, subscriber connections, and finally the params-file installation path — rather than guessing, isolating four independent, real bugs one at a time.
- **DiffDrive angular odometry miscalibration**: the map produced by SLAM was severely smeared, with ghost walls fanning out from turning points. TF chain, bridge configuration, and scan data all checked out individually, so the cause wasn't obvious. Traced to the `DiffDrive` plugin's `wheel_separation` parameter: the value tuned for ROS1's skid-steer plugin (0.45) did not transfer to Gazebo Sim's genuinely different differential-drive kinematic model, causing reported rotation to exceed real rotation by roughly 50%. Diagnosed by commanding a known angular velocity for a fixed duration and directly comparing the resulting odometry-reported yaw against Gazebo's actual model pose. Empirically recalibrated `wheel_separation` to 0.68 (verified to within ~1% error), which fully resolved the smearing.
- **Nav2 base-frame mismatch**: body1 is rotated 90° from the robot's real forward axis, so Nav2 (which assumes +X forward) showed the robot in RViz2 rotated against Gazebo. Switched the Nav2 base frame to dummy_root (true +X forward) and set the AMCL initial pose from a measured map → dummy_root transform instead of the spawn coordinates.
- **Nav2 lifecycle bringup abort**: costmaps failed to activate because AMCL had no pose estimate before the bringup timeout; fixed with set_initial_pose: true and a measured initial pose.
- **Controller performance**: MPPI was too heavy for the setup (missed control-loop rate, robot barely moved); switched to DWB, which restored usable speed.
- **Map display QoS**: RViz2 showed "No map received" because the map topic is TRANSIENT_LOCAL while the display defaulted to volatile durability; matched the display's durability setting.

## Roadmap

Core stack (drive, sensing, SLAM, Nav2 localization and planning) ported and working in simulation. Remaining: traction/odometry tuning, stereo camera, independent 4-wheel drive. See commit history for detailed progress.
