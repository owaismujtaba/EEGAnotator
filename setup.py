from setuptools import setup, find_packages
from typing import List

def get_requirements(file_path: str) -> List[str]:
    '''
    list of requirements
    '''
    requirements = []
    with open(file_path) as file_obj:
        requirements = file_obj.readlines()
        requirements = [req.replace('\n', '') for req in requirements]
    return requirements

setup(
    name='EEG_AUDIO_Anotator',
    version='1.0.0',
    author='Owais Mujtaba Khanday',
    author_email='owais.mujtaba123@gmail.com',
    url='https://github.com/owaismujtaba/EEGAnotator',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GPL-3.0 License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10.14',
    install_requires=get_requirements('requirements.txt'),
    entry_points={
        'console_scripts': [
            'eeganotate=src.main:main',
        ],
    },
    include_package_data=True,
    package_data={
        '': ['*.txt', '*.rst'],
        'classes': ['*.msg'],
        'gui': ['*.msg'],
    },
    license='GPL-3.0'
)
