"""Setup script."""
from __future__ import division, print_function, absolute_import
from setuptools import setup, Extension
import glob
import sysconfig
import sys
suffix = sysconfig.get_config_var('EXT_SUFFIX')
if suffix is None:
    suffix = ".so"

# Borrowing heavily from REBOUND here.
if sys.platform == 'darwin':
    from distutils import sysconfig
    vars = sysconfig.get_config_vars()
    vars['LDSHARED'] = vars['LDSHARED'].replace('-bundle', '-shared')
    extra_link_args = ['-L/usr/local/lib',
                       '-Wl,-install_name,@rpath/liborbit' + suffix]
else:
    extra_link_args = ['-L/usr/local/lib']
liborbitmodule = Extension('liborbit',
                           sources=glob.glob('rebound/src/*.c') +
                           ['ttv_devil/orbit.c'],
                           include_dirs=['rebound/src/',
                                         'ttv_devil/',
                                         '/usr/local/include'],
                           define_macros=[('LIBREBOUND', None)],
                           extra_compile_args=['-Wall',
                                               '-I/usr/local/include',
                                               '-fstrict-aliasing', '-O3',
                                               '-std=c99',
                                               '-Wno-unknown-pragmas',
                                               '-DLIBREBOUND',
                                               '-D_GNU_SOURCE', '-fPIC'],
                           extra_link_args=extra_link_args,
                           libraries=['gsl', 'gslcblas', 'm']
                           )

# Setup!
setup(name='ttv_devil',
      version='0.0.1',
      description='TTV Devil',
      long_description='TTV Devil',
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Topic :: Scientific/Engineering :: Astronomy',
      ],
      url='http://github.com/rodluger/ttv-devil',
      author='Rodrigo Luger',
      author_email='rodluger@uw.edu',
      license='MIT',
      packages=['ttv_devil'],
      install_requires=[
          'numpy>=1.8',
          'matplotlib'
      ],
      include_package_data=True,
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose'],
      ext_modules=[liborbitmodule],
      )
