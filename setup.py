from setuptools import setup, find_packages
import os

setup(name = 'fish_slapping',
      version = '0.1',
      description = 'Server monitoring with Jabber',
      long_description = open(os.path.join(os.path.dirname(__file__), "README.rst")).read(),
      author = "Luis Fagundes",
      author_email = "lhfagundes@hacklab.com.br",
      license = "GPL3",
      packages = find_packages(),
      entry_points = {
          'console_scripts': [
              'fish_slapping_bot = fish_slapping:run_bot',
              ]
          },
      classifiers = [
          'Intended Audience :: System Administrators',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Development Status :: 4 - Beta',
          'Topic :: System',
        ],
      url = 'http://github.com/lfagundes/fish-slapping/',
      
)
