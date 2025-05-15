# BlueROV2 Simulation Control Justfile

# Default configuration
sliders := "false"
debug := "false"
headless := "false"
src_path := "/home/ros/ros2_ws/src"
scripts_path := "/home/ros/ros2_ws/src/scripts"
config_path := "/home/ros/ros2_ws/src/scripts/ros_config.sh"

# Main command - either start or stop the simulation
default:
    @just --list

# Start container.
up_host:
    #!/usr/bin/env bash
    set -eo pipefail

    docker compose up -d

    echo "Container started"

# Build the workspace inside Docker container
build_workspace:
    #!/usr/bin/env bash
    set -eo pipefail

    # Run the setup_workspace.sh script inside the container
    docker exec -it ros2_simulator bash -c "{{scripts_path}}/setup_workspace.sh"

# Start Docker container and run simulation
start_simulation sliders=sliders debug=debug headless=headless:
    #!/usr/bin/env bash
    set -eo pipefail

    # Set logging level based on debug flag
    if [ "{{debug}}" = "true" ]; then
        LOG_LEVEL="debug"
        DEBUG_FLAG="--debug"
    else
        LOG_LEVEL="info"
        DEBUG_FLAG=""
    fi
    
    # Set GUI based on headless flag
    if [ "{{headless}}" = "true" ]; then
        GUI="false"
    else
        GUI="true"
    fi

    # Allow X11 connections from Docker
    xhost +local:docker

    # Create X11 authentication file
    touch /tmp/.docker.xauth
    xauth nlist $DISPLAY | sed -e 's/^..../ffff/' | xauth -f /tmp/.docker.xauth nmerge -

    # Launch the world
    docker exec -di ros2_simulator bash -c "cd {{src_path}} && source {{config_path}} && export RCUTILS_LOGGING_LEVEL=$LOG_LEVEL && ros2 launch $DEBUG_FLAG simulation_world world_launch.py gui:=$GUI"

    # Wait for the world to load
    sleep 5

    # Only position camera if not in headless mode
    if [ "{{headless}}" = "false" ]; then
        docker exec -di ros2_simulator bash -c "gz service -s /gui/move_to/pose --reqtype gz.msgs.GUICamera --reptype gz.msgs.Boolean --timeout 2000 --req 'pose: {position: {x: -1.791294, y: 0.035176, z: 0.396012} orientation: {x: 0.0, y: 0.0, z: 0.0, w: 0.6533}}'"
    fi

    # Spawn the first BlueROV2 model at position (-2,0,0)
    docker exec -di ros2_simulator bash -c "cd {{src_path}} && source {{config_path}} && export RCUTILS_LOGGING_LEVEL=$LOG_LEVEL && ros2 launch $DEBUG_FLAG bluerov2_description upload_bluerov2_launch.py namespace:=bluerov2_1 sliders:={{sliders}} x:=-2.0 y:=0.0 z:=0.0"

    # Spawn the second BlueROV2 model at position (2,0,0) with 90-degree rotation
    docker exec -di ros2_simulator bash -c "cd {{src_path}} && source {{config_path}} && export RCUTILS_LOGGING_LEVEL=$LOG_LEVEL && ros2 launch $DEBUG_FLAG bluerov2_description upload_bluerov2_launch.py namespace:=bluerov2_2 sliders:={{sliders}} x:=2.0 y:=0.0 z:=0.0 yaw:=1.57"

    # Launch the dual wrench control for both robots
    docker exec -di ros2_simulator bash -c "cd {{src_path}} && source {{config_path}} && export RCUTILS_LOGGING_LEVEL=$LOG_LEVEL && ros2 launch $DEBUG_FLAG bluerov2_control dual_wrench_launch.py rviz:=false"

    echo "BlueROV2 simulation started successfully"


# Start the ArduSub SITL simulation. This is done outside of the Docker container.
# Presume that the ArduSub directory is ~/ardupilot/ardupilot
start_SITL_sim mavlink_connection1="udp:127.0.0.1:14550" mavlink_connection2="udp:127.0.0.1:14551":
    #!/usr/bin/env bash
    set -eo pipefail

    # Navigate to the ArduSub directory
    cd ~/ardupilot/ardupilot

    # Start the SITL simulation
    ./Tools/autotest/sim_vehicle.py -v ArduSub -L RATBeach --out={{mavlink_connection1}} --out={{mavlink_connection2}} --map --console



# Start visual servo controller with various configurations
# MAVLink connection URLs:
#   - Physical robot: udpin:192.168.2.1:14550
#   - ArduPilot SITL:   udpin:127.0.0.1:14550
start_visual_servo mode="sim_sim" mavlink_connection="udpin:192.168.2.1:14550":
    #!/usr/bin/env bash
    set -euo pipefail

    # Map mode to launch file and execute appropriate command
    case "{{mode}}" in
        sim_sim)
            docker exec -it ros2_simulator bash -c "\
              cd {{src_path}} && \
              source {{config_path}} && \
              ros2 launch visual_servo bringup_sim_sim.launch.py mavlink_connection:={{mavlink_connection}}\
            "
            ;;
        robot_sim)
            docker exec -it ros2_simulator bash -c "\
              cd {{src_path}} && \
              source {{config_path}} && \
              ros2 launch visual_servo bringup_robot_sim.launch.py mavlink_connection:={{mavlink_connection}}\
            "
            ;;
        webcam_sim)
            docker exec -it ros2_simulator bash -c "\
              cd {{src_path}} && \
              source {{config_path}} && \
              ros2 launch visual_servo bringup_webcam_sim.launch.py mavlink_connection:={{mavlink_connection}}\
            "
            ;;
        robot_robot)
            docker exec -it ros2_simulator bash -c "\
              cd {{src_path}} && \
              source {{config_path}} && \
              ros2 launch visual_servo bringup_robot_robot.launch.py mavlink_connection:={{mavlink_connection}}\
            "
            ;;
        webcam_robot)
            docker exec -it ros2_simulator bash -c "\
              cd {{src_path}} && \
              source {{config_path}} && \
              ros2 launch visual_servo bringup_webcam_robot.launch.py mavlink_connection:={{mavlink_connection}}\
            "
            ;;
        *)
            echo "Invalid mode. Available: sim_sim, robot_sim, webcam_sim, robot_robot, webcam_robot"
            exit 1
            ;;
    esac

    echo "Visual servo controller started in $mode mode"


# Start random movement for leader ROV
start_simulation_leader_random_motion forward_force="5.0" yaw_torque="8.0" turn_duration="1000" interval="2000" runtime="300.0":
    #!/usr/bin/env bash
    set -eo pipefail

    # Run the random movement controller with proper parameter passing
    docker exec -it ros2_simulator bash -c "cd {{src_path}} && source {{config_path}} && ros2 launch random_movement_for_leader random_movement_launch.py forward_force:={{forward_force}} yaw_torque:={{yaw_torque}} turn_duration_ms:={{turn_duration}} interval_between_turns_ms:={{interval}} total_runtime_sec:={{runtime}}"

# Stop Docker container and simulation
stop:
    #!/usr/bin/env bash
    set -eo pipefail

    # Stop and remove the container
    docker compose down

    echo "BlueROV2 simulation stopped"