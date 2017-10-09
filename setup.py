import os
import runpy

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.md')).read()

# Extract the version from unsonic
VERSION = runpy.run_path(os.path.join(here, "unsonic/version.py"))["VERSION"]


def requirements(filename):
    if os.path.exists(filename):
        return [l for l in open(filename).read().splitlines()
                    if not l.startswith("#")]
    else:
        return ""


setup(name='unsonic',
      version=VERSION,
      description='Unsonic, the un-Subsonic music server.',
      long_description=(README + '\n\n' + "*" * 30 + " CHANGES " + "*" * 30 +
                        "\n\n" + CHANGES),
      classifiers=[
          "Intended Audience :: End Users/Desktop",
          "Operating System :: POSIX",
          "Natural Language :: English",
          "Programming Language :: Python",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
          "Development Status :: 3 - Alpha",
          ],
      author='Chris Newton',
      author_email='redshodan@gmail.com',
      url='https://github.com/redshodan/unsonic',
      keywords=["unsonic", "mishmash", "eyed3", "web", "wsgi", "bfg",
                "pylons", "pyramid"],
      packages=find_packages(),
      python_requires='>=3.6',
      include_package_data=True,
      zip_safe=False,
      platforms=["Any"],
      test_suite='unsonic',
      install_requires=requirements("requirements.txt"),
      setup_requires=['pytest-runner'],
      tests_require=requirements("requirements-test.txt"),
      license="GPLv2",
      entry_points={
          'paste.app_factory': ["main = unsonic:main"],
          'console_scripts': ['unsonic = unsonic.__main__:main',
                              'unsonic-server = unsonic:webServe'],
      },
      )
