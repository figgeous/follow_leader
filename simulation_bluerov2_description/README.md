# BlueROV2 Description Package

This package contains the description files for the BlueROV2 underwater vehicle, including URDF models, meshes, and launch files for simulation in Gazebo.

![BlueROV2](bluerov2.jpg)

## Package Structure

### URDF Files (`urdf/`)
- `bluerov2.xacro`: Main robot description file that defines the base link, physical properties (mass, inertia, buoyancy), and includes other component files. It sets up the robot's dimensions, center of gravity, center of buoyancy, and includes necessary Gazebo plugins for simulation.
- `thrusters.xacro`: Defines the six-thruster configuration for the BlueROV2 using the T200 thruster model. It includes macros for creating thruster links and joints, and configures the thruster positions and orientations according to the BlueROV2 design.
- `hydrodynamics.xacro`: Contains hydrodynamic parameters for underwater simulation based on research papers about the BlueROV2. It defines added mass coefficients, linear and quadratic damping coefficients, and other hydrodynamic properties needed for realistic underwater behavior.
- `sensors.xacro`: Defines sensors including two IMUs (MPU9250 and LSM9DS1), a downward-facing camera, and a Ping360 scanning sonar. It configures sensor properties like update rates, noise parameters, and visual representations.
- `demo_world.sdf`: SDF file for the demo world environment that sets up an underwater scene with appropriate physics properties, lighting, and visual elements for underwater simulation.
- `snippets/`: Contains URDF snippets for reuse in different robot configurations or for modular robot building.

### Launch Files (`launch/`)
- `upload_bluerov2_launch.py`: Main launch file for loading the BlueROV2 model into Gazebo with various configuration options. It sets up ROS-Gazebo bridges for sensors, thrusters, and pose information, and configures ground truth data if requested.
- `state_publisher_launch.py`: Launches the robot state publisher that broadcasts the robot's joint states and transforms. It processes the XACRO files and publishes the robot model to the ROS parameter server.
- `world_launch.py`: Launches the Gazebo world with the BlueROV2. It sets up the ocean environment, configures physics parameters, and creates necessary transforms between world frames.
- `manual.yaml`: Configuration file for manual control using sliders. It defines the thruster control topics and their value ranges for interactive testing and manual operation of the vehicle.

### 3D Models (`meshes/`)
- `bluerov2_noprop.dae`: Main body mesh without propellers, representing the BlueROV2 frame, electronics enclosure, and structural components.
- `bluerov2_propcw.dae/ive`: Clockwise propeller meshes used for thrusters 1, 2, and 5 in the standard BlueROV2 configuration. Available in both COLLADA (.dae) and Inventor (.ive) formats for compatibility.
- `bluerov2_propccw.dae/ive`: Counter-clockwise propeller meshes used for thrusters 3, 4, and 6. The counter-rotation helps balance torque effects during operation.
- `ping360_sonar.dae`: Mesh for the Ping360 scanning sonar sensor, which provides obstacle detection and mapping capabilities underwater.

### Specifications (`specs/`)
- `T200-Public-Performance-Data-10-20V-September-2019.xlsx`: Performance data for the T200 thrusters from Blue Robotics, including thrust curves, power consumption, and efficiency metrics at different voltage levels.
- `hydro.py`: Python script for hydrodynamic calculations and visualization. It implements models from research papers to calculate and plot hydrodynamic coefficients for the BlueROV2, helping to validate the parameters used in simulation.

### Hooks (`hooks/`)
- `resource_paths.dsv.in`: Resource path configuration for the package that ensures the package resources (meshes, models, etc.) are properly found by ROS 2 and Gazebo during runtime.

## Usage

### Loading the BlueROV2 Model
To load the BlueROV2 model in Gazebo, use the `upload_bluerov2_launch.py` launch file:

```bash
ros2 launch bluerov2_description upload_bluerov2_launch.py
```

### Launch Arguments
The launch files support several arguments:
- `namespace`: Namespace for the robot (default: 'bluerov2')
- `ground_truth`: Enable ground truth odometry (default: true)
- `sliders`: Enable manual control sliders (default: false)
- `camera`: Enable camera (default: true)
- `gazebo_world_name`: Name of the Gazebo world to use (default: 'none')

### Initial Pose
You can set the initial pose of the robot using the following arguments:
- `x`, `y`, `z`: Position coordinates
- `roll`, `pitch`, `yaw`: Orientation angles

## Features
- Accurate physical model of the BlueROV2 with proper mass, inertia, and buoyancy
- Realistic thruster configuration with T200 thruster performance data
- Sensor suite including IMUs, camera, and sonar
- Hydrodynamic effects for underwater simulation
- ROS 2 and Gazebo integration

## Dependencies
- ROS 2
- Gazebo
- simple_launch package

## License
MIT License (see package.xml)

## Maintainer
Olivier Kermorgant (olivier.kermorgant@ec-nantes.fr) 