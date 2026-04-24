import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_path = get_package_share_directory('surveillance_robot')
    urdf_file = os.path.join(pkg_path, 'urdf', 'robot.urdf.xacro')

    robot_description = ParameterValue(
        Command(['xacro ', urdf_file]),
        value_type=str
    )

    return LaunchDescription([

        # 1. Gazebo avec le monde maison
        ExecuteProcess(
            cmd=['gz', 'sim', '-r',
                 os.path.join(pkg_path, 'worlds', 'house.sdf')],
            output='screen'
        ),

        # 2. Robot state publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{
                'robot_description': robot_description,
                'use_sim_time': True
            }],
            output='screen'
        ),

        # 3. Spawne le robot (attend 3s que Gazebo soit prêt)
        TimerAction(
            period=3.0,
            actions=[
                Node(
                    package='ros_gz_sim',
                    executable='create',
                    arguments=[
                        '-name', 'surveillance_robot',
                        '-topic', 'robot_description',
                        '-x', '0', '-y', '0', '-z', '0.1'
                    ],
                    output='screen'
                ),
            ]
        ),

        # 4. Bridge ROS2 <-> Gazebo (attend 4s)
        TimerAction(
            period=4.0,
            actions=[
                Node(
                    package='ros_gz_bridge',
                    executable='parameter_bridge',
                    arguments=[
                        '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
                        '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
                        '/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
                        '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
                        '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
                    ],
                    output='screen'
                ),
            ]
        ),
    ])