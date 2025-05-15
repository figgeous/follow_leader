#!/bin/bash

# ROS 2 distribution configuration
# Change this value to match your installed ROS 2 distribution
ROS_DISTRO="jazzy"

# Workspace path configuration
ROS_WORKSPACE="$HOME/ros2_ws"

# Gazebo version configuration
export GZ_VERSION="harmonic"

# Add gazebo_apriltag models to Gazebo resource path
export GZ_SIM_RESOURCE_PATH="$ROS_WORKSPACE/src/gazebo_apriltag/models"

# Source ROS distribution setup file
source /opt/ros/${ROS_DISTRO}/setup.bash

echo "Sourced ROS 2 distribution"

# Source the workspace if it exists
if [ -f "$ROS_WORKSPACE/install/setup.bash" ]; then
  echo "Sourced ros2_ws workspace"
  source $ROS_WORKSPACE/install/setup.bash
fi

