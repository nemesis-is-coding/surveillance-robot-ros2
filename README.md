# 🤖 Robot de Surveillance Autonome — ROS2 Jazzy

Robot mobile simulé dans Gazebo qui patrouille automatiquement un périmètre,
détecte les intrusions via YOLOv8 et déclenche une alarme en temps réel.

---

## 🛠️ Stack technique

| Outil | Rôle |
|---|---|
| ROS2 Jazzy | Framework robotique |
| Gazebo Harmonic | Simulation physique 3D |
| URDF / Xacro | Modélisation du robot |
| Nav2 | Navigation autonome |
| YOLOv8 | Détection de personnes |
| Python / rclpy | Programmation des nœuds |

---

## 📁 Structure du projet
robot_surveillance_ws/
└── src/
└── surveillance_robot/
├── urdf/
│   └── robot.urdf.xacro      # Modèle du robot (châssis, roues, lidar, caméra)
├── launch/
│   ├── gazebo.launch.py      # Lance Gazebo + robot
│   ├── nav2.launch.py        # Lance Gazebo + Nav2 + patrouille
│   └── display.launch.py     # Lance RViz2 seul
├── worlds/
│   └── house.sdf             # Monde Gazebo (maison avec pièces)
├── maps/
│   └── map.yaml              # Carte de navigation
├── config/
│   └── nav2_params.yaml      # Paramètres Nav2
├── scripts/
│   ├── patrol.py             # Patrouille autonome en boucle
│   ├── detection.py          # Détection YOLOv8 via caméra
│   ├── alarm.py              # Système d'alarme
│   └── frame_fix.py          # Correction des frames ROS2/Gazebo
├── CMakeLists.txt
└── package.xml

---

## ⚙️ Prérequis

- Ubuntu 24.04
- ROS2 Jazzy
- Python 3.12
- WSL2 (si Windows)

---

## 🚀 Installation

### 1. Installe ROS2 Jazzy

```bash
sudo apt update && sudo apt install locales -y
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8

sudo apt install software-properties-common curl -y
sudo add-apt-repository universe
export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F'"' '{print $4}')
curl -L -o /tmp/ros2-apt-source.deb \
  "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"
sudo dpkg -i /tmp/ros2-apt-source.deb

sudo apt update && sudo apt upgrade -y
sudo apt install ros-jazzy-desktop ros-dev-tools -y

echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### 2. Installe les dépendances ROS2

```bash
sudo apt install \
  ros-jazzy-navigation2 \
  ros-jazzy-nav2-bringup \
  ros-jazzy-slam-toolbox \
  ros-jazzy-ros-gz \
  ros-jazzy-joint-state-publisher-gui \
  ros-jazzy-robot-state-publisher \
  ros-jazzy-xacro \
  ros-jazzy-cv-bridge \
  python3-colcon-common-extensions \
  python3-rosdep -y
```

### 3. Installe YOLOv8

```bash
# Installe pip
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py --break-system-packages
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Installe YOLOv8 et downgrade numpy pour compatibilité ROS2
pip install ultralytics --break-system-packages
pip install "numpy<2" --break-system-packages
```

### 4. Clone et compile le projet

```bash
mkdir -p ~/robot_surveillance_ws/src
cd ~/robot_surveillance_ws/src
git clone https://github.com/nemesis-is-coding/surveillance-robot-ros2.git surveillance_robot

cd ~/robot_surveillance_ws
colcon build
echo "source ~/robot_surveillance_ws/install/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

---

## ▶️ Lancement

### Option A — Simulation simple avec patrouille

**Terminal 1 — Gazebo + robot :**
```bash
cd ~/robot_surveillance_ws
source install/setup.bash
ros2 launch surveillance_robot gazebo.launch.py
```

**Terminal 2 — Patrouille autonome :**
```bash
ros2 run surveillance_robot patrol.py
```

**Terminal 3 — Système d'alarme :**
```bash
ros2 run surveillance_robot alarm.py
```

---

### Option B — Avec Nav2 (navigation avancée)

**Terminal 1 — Tout en un :**
```bash
ros2 launch surveillance_robot nav2.launch.py
```

**Terminal 2 — Alarme :**
```bash
ros2 run surveillance_robot alarm.py
```

---

### Option C — Détection YOLOv8

**Terminal — Détection sur image :**
```bash
python3 -c "
from ultralytics import YOLO
model = YOLO('yolov8n.pt')
results = model('/tmp/test.jpg')
print('Détections:', [model.names[int(b.cls[0])] for r in results for b in r.boxes])
"
```

**Terminal — Détection via flux caméra ROS2 :**
```bash
ros2 run surveillance_robot detection.py
```

---

### Téléopération clavier (contrôle manuel)

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args --remap cmd_vel:=/cmd_vel
```

| Touche | Action |
|---|---|
| `i` | Avancer |
| `,` | Reculer |
| `j` | Tourner gauche |
| `l` | Tourner droite |
| `k` | Stop |

---

### Simuler une intrusion manuellement

```bash
ros2 topic pub /intrusion_detected std_msgs/msg/Bool "data: true" --once
```

---

### Visualisation RViz2

```bash
ros2 launch nav2_bringup rviz_launch.py
```

---

## 🔍 Topics ROS2 principaux

| Topic | Type | Description |
|---|---|---|
| `/cmd_vel` | Twist | Commandes de mouvement |
| `/scan` | LaserScan | Données lidar |
| `/odom` | Odometry | Position du robot |
| `/camera/image_raw` | Image | Flux caméra |
| `/intrusion_detected` | Bool | Alerte d'intrusion |
| `/intrusion_label` | String | Label de l'objet détecté |

---

## 🏗️ Architecture du système
Gazebo (simulation)
├── /scan ──────────────→ Nav2 (navigation)
├── /odom ──────────────→ frame_fix → Nav2
└── /camera/image_raw ──→ detection.py (YOLOv8)
↓
/intrusion_detected
↓
alarm.py 🚨
Nav2 ──→ /cmd_vel ──→ Gazebo (mouvement robot)
patrol.py ──→ /cmd_vel ──→ Gazebo (patrouille)


## Auteur
BOUGHENOU Akli Mahdi — Projet robotique 2026
