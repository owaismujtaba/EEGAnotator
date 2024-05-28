from setuptools import setup, find_packages
from typing import List

HYPEN_E_DOT = '-e .'

def get_requirements(file_path:str)->List[str]:
    '''
        list of requirements
    '''
    requirements = []
    with open(file_path) as file_obj:
        requirements = file_obj.readlines()
        requirements = [req.replace('\n', '') for req in requirements]

        if HYPEN_E_DOT in requirements:
            requirements.remove(HYPEN_E_DOT)

setup(
    name='EEG_AUDIO_Anotator',
    version='1.0.0',
    author = 'Owais Mujtaba Khanday',
    author_email = 'owais.mujtaba123@gmail.com',
    packages = find_packages(),
    install_requires = get_requirements('requirements.txt')
    entry_points={
        "console_scripts": [
            "eeganotate=src.run:main",
        ]
    }
)
