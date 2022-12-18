from setuptools import setup

with open('requirements.txt', 'r') as fp:
  installrequires = fp.readlines()

setup(
    name='motion_monitor',
    description='Simple tool to read the state of a motion sensor using an Arduino compatible board and report the status over MQTT',
    version='0.1.0',
    packages=['motion_monitor'],
    install_requires=installrequires,
    entry_points={
        'console_scripts': [
            'motion-monitor = motion_monitor.__main__:cli',
        ],
    },
)
