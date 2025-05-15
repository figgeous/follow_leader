cmake_minimum_required(VERSION 3.5)
project(simulation_world)

find_package(ament_cmake REQUIRED)
find_package(geometry_msgs REQUIRED)

install(DIRECTORY launch worlds config DESTINATION share/${PROJECT_NAME})

ament_package()
