cmake_minimum_required(VERSION 3.5)
project(random_movement_for_leader)

find_package(ament_cmake REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(rclpy REQUIRED)

# Install the random movement node
install(PROGRAMS
  random_movement.py
  DESTINATION lib/${PROJECT_NAME}
)

# Install launch files
install(DIRECTORY
  launch
  DESTINATION share/${PROJECT_NAME}
)

ament_package() 