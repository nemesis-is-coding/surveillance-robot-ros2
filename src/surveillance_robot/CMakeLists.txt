cmake_minimum_required(VERSION 3.8)
project(surveillance_robot)

find_package(ament_cmake REQUIRED)

install(DIRECTORY urdf launch worlds maps config scripts
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS
  scripts/patrol.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()