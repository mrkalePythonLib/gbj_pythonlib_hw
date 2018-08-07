#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup function for the package."""

from setuptools import setup

setup(
  name='gbj_pythonlib_hw',
  version='1.0.0',
  description='Python libraries for hardware support.',
  long_description='Modules suitable for utilizing Pi microcomputers, \
system buses, and sensors in python console applications.',
  classifiers=[
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 2.7',
    'Topic :: System :: Monitoring',
  ],
  keywords='pi, orangepi, raspberrypi, nanopi',
  url='http://github.com/mrkalePythonLib/gbj_pythonlib_hw',
  author='Libor Gabaj',
  author_email='libor.gabaj@gmail.com',
  license='MIT',
  packages=['gbj_pythonlib_hw'],
  install_requires=['pyA20'],
  include_package_data=True,
  zip_safe=False
)
