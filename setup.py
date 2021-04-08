#  Copyright (c) 2021. fit&healthy 365

from setuptools import setup

setup(
    name='FH365',
    version='0.3',
    packages=[
        'FitCalender',
        'Tools'
    ],
    url='',
    license='',
    author='Sr.up',
    author_email='Ncicartier@gmail.com',
    description='Fit&Healthy 365 calender app',
    python_requires='>=3.8',
    install_requires=[
        'flask',
        'mysql-connector-python',
        'flask_bootstrap'
      ]
)
