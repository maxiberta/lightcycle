from setuptools import setup, find_packages

requires = [
    'numpy',
    'nose',
    'coverage',
    ]

setup(name='lightcycle',
      version='0.0',
      description='A simple AI lightcycle game engine',
      classifiers=[
        "Programming Language :: Python",
        ],
      author='',
      author_email='',
      url='',
      keywords='web python tron',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='lightcycle',
      install_requires=requires,
      )
