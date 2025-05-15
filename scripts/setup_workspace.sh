#!/bin/bash

# Fix for ROS2 setup scripts that use undefined variables
export AMENT_TRACE_SETUP_FILES=

# Navigate to the workspace root
ROS_WORKSPACE="$HOME/ros2_ws"
cd "$ROS_WORKSPACE"

source "$ROS_WORKSPACE/src/scripts/ros_config.sh"

# Install dependencies
echo "Installing dependencies..."
rosdep update
rosdep install --from-paths src --ignore-src -r -y

# Clean build and install folders
echo "Cleaning build and install folders..."
rm -rf build/ install/ log/

# Build the workspace
echo "Building the workspace..."
colcon build --symlink-install

# Source the workspace
echo "Sourcing the workspace..."
source "$ROS_WORKSPACE/src/scripts/ros_config.sh"