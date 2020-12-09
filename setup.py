from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()

setup(name='pyRigolCtl',
      version='0.1',
      description='Provides an interface to Rigol DP8xx power supplies.',
      long_description=readme(),
      author='Sean Griffin',
      author_email='sean.c.griffin@gmail.com',
      packages=['pyRigolCtl'],
      install_requires=['pyvisa', 'pyvisa-py', 'pyyaml','numpy'],
      )
