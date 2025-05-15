# Follow the Leader

This repository contains a collection of ROS2 packages for controlling and simulating one or two BlueROV2 underwater vehicle(s) using Docker.
The main objective is to allow a Follower ROV to track a Leader ROV using visual servoing, centered around AprilTags attached to the Leader's chassis.
The recipes in this file will allow you to control an ArduPilot-enabled ROV either in Software-in-the-Loop, or in the physical world. Additionally, you
a Follower and Leader ROV can be run in a Gazebo simulation. 

## Quick Start

1. Clone the repository:
```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
git clone --recurse-submodules <repository-url>
```

2. Build the workspace:
```bash
just build_workspace
```

### Start the simulation

3. Start the simulation:
```bash
# Basic simulation
just start_simulation
```

### Start ROV control

3. Start the visual_servo:
```bash
just start_visual_servo robot_robot
```


## Available Commands

- `just build_workspace` - Build the ROS2 workspace inside Docker
- `just start_simulation [sliders=false] [debug=false] [headless=false]` - Start the BlueROV2 simulation
- `just start_visual_servo [mode="sim_sim"] [mavlink_connection="udpin:192.168.2.1:14550"]` - Start visual servo controller with various configurations
  The visual servo controller supports different run configurations:
    - `sim_sim`: Both leader and follower ROVs are simulated
    - `robot_sim`: Leader ROV is physical, follower is simulated
    - `webcam_sim`: Leader uses webcam feed, follower is simulated
    - `robot_robot`: Both leader and follower ROVs are physical
    - `webcam_robot`: Leader uses webcam feed, follower is physical

- `just start_SITL_sim [mavlink_connection1="udp:127.0.0.1:14550"] [mavlink_connection2="udp:127.0.0.1:14551"]` - Start ArduSub SITL simulation
- `just start_simulation_leader_random_motion [forward_force="5.0"] [yaw_torque="8.0"] [turn_duration="1000"] [interval="2000"] [runtime="60.0"]` - Start random movement for leader ROV
- `just stop` - Stop the simulation and Docker container

## Prerequisites

- Docker Engine
- X11 (for GUI support)
- Git
- Just (command runner)

## System Requirements

- Docker Engine (latest version)
- Ubuntu 24.05 or later. If you don't have Ubuntu, you can use:
  - Windows: WSL2 with Ubuntu
  - Mac: Docker Desktop with Ubuntu container
  - Any OS: VirtualBox with Ubuntu 22.04

## Configuration

The simulation uses Docker with ROS2 Jazzy and Gazebo Harmonic. All necessary dependencies are included in the Docker image.

## Acknowledgements

Thanks to [Olivier Kermorgant](https://github.com/figgeous/ArteSuaveClient/issues/10) for BlueROV2 description and control packages. 

Thanks to [Olaya Álvarez Tuñón](https://github.com/olayasturias) for the helping me connect with the physical robot.

Thanks to [Andrzej Wąsowski](https://github.com/wasowski) for project supervision.

## License

Each submodule may have its own license. Please refer to the individual submodule repositories for license information.
