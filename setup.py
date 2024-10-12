# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in acca/__init__.py
from acca import __version__ as version

setup(
	name='acca',
	version=version,
	description='App for managing ACCA based Institutions.',
	author='Unilink Enterprise',
	author_email='erp@unilinkenterprise.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
