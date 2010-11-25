# -*- coding: utf-8 -*-
"""
This module contains the tool of incf.abstractsubmission
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.0'

long_description = (
    read('README.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('incf', 'abstractsubmission', 'README.txt')
    + '\n' +
    'Contributors\n'
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n' +
    'Download\n'
    '********\n')

tests_require = ['zope.testing']

setup(name='incf.abstractsubmission',
      version=version,
      description="Submission Folder and Abstract type",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='Congress Abstract Submission',
      author='Raphael Ritz',
      author_email='raphael.ritz@incf.org',
      url='http://io.incf.ki.se/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['incf', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        # -*- Extra requirements: -*-
                        'Products.ATExtensions',
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite='incf.abstractsubmission.tests.test_docs.test_suite',
      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins=["ZopeSkel"],
      )
