from setuptools import setup

package_name = 'rossi_plugin'
setup(
    name=package_name,
    version='0.1.0',
    package_dir={'': 'src'},
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name + '/resource', ['resource/main.ui']),
        ('share/' + package_name + '/resource', ['resource/library.ui']),
        ('share/' + package_name + '/resource', ['resource/settings.ui']),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name, ['plugin.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    author='Sebastian Rossi',
    maintainer='Sebastian Rossi',
    maintainer_email='rossi@isse.de',
    keywords=['ROS'],
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
    description=(
        'A Python GUI plugin to develop ROS 2 projects.'
    ),
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'rossi_plugin = rossi_plugin.main:main',
        ],
    },
)
