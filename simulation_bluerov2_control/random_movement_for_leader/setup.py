from setuptools import setup
import os
from glob import glob

package_name = 'random_movement_for_leader'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='user@todo.todo',
    description='BlueROV2 waypoint navigation and random movement control',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'random_movement = random_movement_for_leader.random_movement:main',
        ],
    },
    scripts=['random_movement_for_leader/random_movement.py'],
) 