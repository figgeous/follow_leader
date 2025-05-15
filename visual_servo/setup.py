#!/usr/bin/env python3
from setuptools import setup, find_packages
from glob import glob

package_name = 'visual_servo'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            [f'resource/{package_name}']),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        ('share/' + package_name + '/params', glob('params/*.yaml')),
    ],
    install_requires=[
        'setuptools',
        'pupil-apriltags',
    ],
    zip_safe=True,
    maintainer='Thomas O\'Neill',
    maintainer_email='thomas.oneill@gmail.com',
    description='A unified AprilTag visual‐servo node for sim & real',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'visual_servo_node = visual_servo.node:main',
        ],
    },
)
