#!/usr/bin/env python
# -*- coding:utf-8 -*-
from setuptools import setup, find_packages
import os

setup(name='fiee-dorsale',
      version='0.0.7',
      description=u'Django base classes to handle management data like site, creation & change date & user',
      keywords='site group owner changed created mine',
      author='Henning Hraban Ramm',
      author_email='hraban@fiee.net',
      license='BSD',
      url='https://github.com/fiee/fiee-dorsale',
      download_url='https://github.com/fiee/fiee-dorsale/tarball/master',
      package_dir={
                   'dorsale': 'dorsale',
                   'siteprofile': 'siteprofile',
                   },
      packages=find_packages(),
      include_package_data = True,
      package_data = {'': ['*.rst', 'locale/*/LC_MESSAGES/*.*', 'templates/*/*.*', 'templates/*/*/*.*', ]},
      # see http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Topic :: Utilities',
                   'Natural Language :: English',
                   'Natural Language :: German',],
      install_requires=['Django>=1.6', 'django-registration', 'django-async-messages'],
      zip_safe=False,
      )
