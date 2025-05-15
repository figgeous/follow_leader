FROM osrf/ros:jazzy-desktop-full

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV GZ_VERSION=harmonic
ARG DISTRO=jazzy
ARG USERNAME=ros
ARG USER_UID=1000
ARG USER_GID=1000
ARG WORKSPACE=ros2_ws

# Update and install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    lsb-release \
    gnupg \
    git \
    python3-pip \
    python3-rosdep \
    python3-colcon-common-extensions \
    ros-${DISTRO}-rmw-cyclonedds-cpp \
    ros-${DISTRO}-teleop-twist-joy \
    ros-${DISTRO}-joy \
    ros-${DISTRO}-xacro \
    ros-${DISTRO}-ros2-control \
    ros-${DISTRO}-ros2-controllers \
    ros-${DISTRO}-joint-state-publisher \
    ros-${DISTRO}-joint-state-publisher-gui \
    ros-${DISTRO}-rviz2 \
    ros-${DISTRO}-simple-launch \
    ros-${DISTRO}-slider-publisher \
    ros-${DISTRO}-mavros \
    ros-${DISTRO}-mavros-msgs \
    ros-${DISTRO}-mavros-extras \
    ros-${DISTRO}-usb-cam \
    geographiclib-tools \
    nano \
    sudo \
    x11-apps \
    mesa-utils \
    just \
    && geographiclib-get-geoids egm96-5 \
    && geographiclib-get-gravity egm96 \
    && geographiclib-get-magnetic emm2015 \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --break-system-packages -r /tmp/requirements.txt

# Install Gazebo Harmonic
RUN curl -sSL https://packages.osrfoundation.org/gazebo.gpg -o /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        gz-harmonic \
    && rm -rf /var/lib/apt/lists/*

# Install ROS2-Gazebo integration packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-${DISTRO}-ros-gz \
    ros-${DISTRO}-gz-ros2-control \
    && rm -rf /var/lib/apt/lists/*

# Install GStreamer packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    libgstreamer-plugins-bad1.0-dev \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    gstreamer1.0-tools \
    gstreamer1.0-x \
    gstreamer1.0-alsa \
    gstreamer1.0-gl \
    gstreamer1.0-gtk3 \
    gstreamer1.0-qt5 \
    gstreamer1.0-pulseaudio \
    && rm -rf /var/lib/apt/lists/*


# Create a non-root user with proper handling of existing users/groups
RUN if getent group ${USER_GID} > /dev/null; then \
        echo "Group with GID ${USER_GID} already exists"; \
    else \
        groupadd --gid ${USER_GID} ${USERNAME}; \
    fi \
    && if id -u ${USER_UID} > /dev/null 2>&1; then \
        echo "User with UID ${USER_UID} already exists"; \
        usermod -l ${USERNAME} $(id -nu ${USER_UID}); \
    else \
        useradd --uid ${USER_UID} --gid ${USER_GID} -m ${USERNAME} || useradd -l -m -g ${USER_GID} ${USERNAME}; \
    fi \
    && echo ${USERNAME} ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/${USERNAME} \
    && chmod 0440 /etc/sudoers.d/${USERNAME}

# Set up environment for the user
ENV HOME=/home/${USERNAME}
USER ${USERNAME}
WORKDIR /home/${USERNAME}/${WORKSPACE}/src

# Add user to necessary groups for GUI applications
RUN sudo usermod -a -G render,video,audio,input ${USERNAME} || true

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]