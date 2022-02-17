from setuptools import setup

setup(
    name='PALS',
    version='2.0.3',
    packages=['PALS'],
    url='https://github.com/npnl/PALS',
    license='MIT',
    author='AlexandreHutton',
    author_email='ahutton@usc.edu',
    description='Pipeline for Analyzing Lesions after Stroke',
    entry_points={
        'console_scripts': ['PALS=PALS.pals_workflow:main']
    }
)
