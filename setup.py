#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

from __future__ import division, print_function, absolute_import

import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
        README = readme.read()

        # allow setup.py to be run from any path
        os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

        setup(
                name='django-enums',
                version='0.2.0',
                include_package_data=True,
                packages=find_packages(exclude=['tests*', 'docs*']),
                install_requires=['django'],
                license='MIT License',
                description='A simple Enum class and EnumField for Django models.',
                long_description=README,
                keywords=['django', 'enum', 'field', 'status', 'state', 'choices', 'form', 'model'],
                url='https://github.com/galonsky/django-enums',
                download_url='https://github.com/galonsky/django-enums/tarball/{version}'.format(version='0.2.0'),
                author='Hikaru Horie, Alex Galonsky',
                author_email='hikaru@horie.to',
                platforms=['any'],
                classifiers=[
#                        'Development Status :: Beta',
                        'Environment :: Web Environment',
                        'Framework :: Django',
                        'Framework :: Django :: 1.8',
                        'Framework :: Django :: 1.9',
                        'Framework :: Django :: 1.10',
                        'Intended Audience :: Developers',
                        'License :: OSI Approved :: MIT License',
                        'Operating System :: OS Independent',
                        'Programming Language :: Python',
                        # Replace these appropriately if you are stuck on Python 2.
                        'Programming Language :: Python :: 3',
                        'Topic :: Internet :: WWW/HTTP',
                        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
                        ],
                )
