# 🤖 Robot de Surveillance Autonome — ROS2 Jazzy

Robot mobile simulé dans Gazebo qui patrouille automatiquement un périmètre,
détecte les intrusions via YOLOv8 et déclenche une alarme.

## Stack technique
- ROS2 Jazzy
- Gazebo Harmonic
- Nav2 (navigation autonome)
- YOLOv8 (détection de personnes)
- Python / rclpy

## Structure du projet
surveillance_robot/
├── urdf/         # Modèle du robot
├── launch/       # Fichiers de lancement
├── worlds/       # Monde Gazebo
├── maps/         # Carte de navigation
├── config/       # Paramètres Nav2
└── scripts/      # Nœuds Python (patrouille, détection, alarme)

## Lancement
# Gazebo
ros2 launch surveillance_robot gazebo.launch.py

# Patrouille autonome
ros2 run surveillance_robot patrol.py

## Auteur
Nemesis — Projet robotique 2026
