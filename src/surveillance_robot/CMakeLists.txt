cmake_minimum_required(VERSION 3.8)
project(surveillance_robot)

find_package(ament_cmake REQUIRED)

install(DIRECTORY urdf launch worlds maps config scripts
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS
  scripts/patrol.py
  scripts/detection.py
  scripts/alarm.py
  DESTINATION lib/${PROJECT_NAME}
)

install(PROGRAMS
  scripts/patrol.py
  scripts/detection.py
  scripts/alarm.py
  scripts/frame_fix.py
  DESTINATION lib/${PROJECT_NAME}
)
ament_package()
