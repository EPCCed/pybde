from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()
        
setup(name='pybde',
      version='0.1',
      description='Binary Delay Equation simulator',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Scientific/Engineering',
        'Operating System :: OS Independent',
      ],
      keywords='BDE, binary, delay, equations, solver, simulator',
      url='https://github.com/EPCCed/pynmmso/wiki/pybde',
      author='Ally Hume',
      author_email='a.hume@epcc.ed.ac.uk',
      license='MIT',
      packages=['pybde'],
      install_requires=[
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
