from setuptools import setup

setup(
    name='PALS',
    version='2.0.10',
    packages=['PALS'],
    url='https://github.com/npnl/PALS',
    license='MIT',
    author='AlexandreHutton',
    author_email='erendizt@usc.edu',
    description='Pipeline for Analyzing Lesions after Stroke',
    setup_requires=['wheel'],
    install_requires=[
        'bids',
        'nibabel>=3.2.1',
        'numpy>=1.2.1',
        'pandas>=1.3.2',
        'scipy>=1.7.1',
        'nipype>=1.7.0',
        'bidsio@git+https://github.com/npnl/bidsio@main',
        'matplotlib'
    ],
    entry_points={
        'console_scripts': ['PALS=run_pals:main']
    }
)
