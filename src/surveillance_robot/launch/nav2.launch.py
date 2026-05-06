import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_path = get_package_share_directory('surveillance_robot')
    nav2_bringup = get_package_share_directory('nav2_bringup')
    urdf_file = os.path.join(pkg_path, 'urdf', 'robot.urdf.xacro')
    map_file = os.path.join(pkg_path, 'maps', 'map.yaml')
    params_file = os.path.join(pkg_path, 'config', 'nav2_params.yaml')

    robot_description = ParameterValue(
        Command(['xacro ', urdf_file]),
        value_type=str
    )

    return LaunchDescription([

        # 1. Gazebo
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

        # 3. Spawne le robot
        TimerAction(period=3.0, actions=[
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
        ]),

        # 4. Bridge ROS2 <-> Gazebo avec remapping des frames
        TimerAction(period=4.0, actions=[
            Node(
                package='ros_gz_bridge',
                executable='parameter_bridge',
                arguments=[
                    '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
                    '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
                    '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
                    '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
                ],
                output='screen'
            ),
            # Nœud qui corrige les frame_id
            Node(
                package='surveillance_robot',
                executable='frame_fix.py',
                output='screen'
            ),
        ]),

        # 5. Nav2
        TimerAction(period=6.0, actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(nav2_bringup, 'launch', 'bringup_launch.py')
                ),
                launch_arguments={
                    'map': map_file,
                    'use_sim_time': 'true',
                    'params_file': params_file,
                }.items()
            ),
        ]),

        # 6. Nœud de patrouille (démarre après Nav2)
        TimerAction(period=15.0, actions=[
            Node(
                package='surveillance_robot',
                executable='patrol.py',
                output='screen'
            ),
        ]),
    ])