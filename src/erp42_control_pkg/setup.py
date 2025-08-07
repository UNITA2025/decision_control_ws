from setuptools import setup, find_packages
from glob import glob

package_name = 'erp42_control_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(include=[package_name, f'{package_name}.*']),
    package_dir={'': '.'},
    data_files=[
        ('share/ament_index/resource_index/packages',
            [f'resource/{package_name}']),
        (f'share/{package_name}', ['package.xml']),
        (f'share/{package_name}/launch', glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='moonshot',
    maintainer_email='ky942400@gmail.com',
    description='ERP42 control node with serial interface',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'ErpSerialHandler_node = erp42_control_pkg.ErpSerialHandler:main',
            'ErpControlTest_node = erp42_control_pkg.ErpControlTest:main',

        ],
    },
)
