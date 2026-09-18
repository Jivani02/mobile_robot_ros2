from setuptools import find_packages, setup

package_name = 'mobile_robot'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/talk_listen.launch.py','launch/display.launch.py']),
        ('share/' + package_name + '/launch', ['launch/gazebo.launch.py']),
        ('share/' + package_name + '/urdf', ['urdf/mobile_robot.urdf']),
        ('share/' + package_name + '/meshes', [
                'meshes/Body1.stl',
                'meshes/front_left_wheel_1__Body1.stl',
                'meshes/front_right_wheel_1__Body1.stl',
                'meshes/reae_right_wheel_1__Body1.stl',
                'meshes/rear_left_wheel_1__Body1.stl',
         ]),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='jivani02',
    maintainer_email='hirenjivani02@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': ['talker = mobile_robot.talker:main',
                            'listner = mobile_robot.listner:main',
        ],
    },
)
