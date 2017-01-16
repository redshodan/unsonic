import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

requires = [
    'pyramid',
    'SQLAlchemy',
    'transaction',
    'pyramid',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'zope.sqlalchemy',
    'waitress',
    'pastedeploy',
    'paste',
    'psycopg2',
    'xmltodict',
    # 'mishmash',
    ]

setup(name='unsonic',
      version='0.0',
      description='Unsonic, the un-music server',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Intended Audience :: End Users/Desktop",
        "Operating System :: POSIX",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Chris Newton',
      author_email='redshodan@gmail.com',
      url='https://bitbucket.org/redshodan/unsonic',
      keywords=["unsonic", "mishmash", "eyed3", "web", "wsgi", "bfg",
                "pylons", "pyramid"],
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      platforms=["Any"],
      test_suite='unsonic',
      install_requires=requires,
      license="GPLv2",
      entry_points="""\
      [paste.app_factory]
      main = unsonic:main
      [console_scripts]
      """,
      )
