import os
import tempfile
from distutils.errors import DistutilsExecError
from glob import glob
from shutil import rmtree
from sys import platform

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext
from setuptools.command.install_lib import install_lib

ext_clean = os.environ.get('ASSESS_EXT_CLEAN')

assess_ext_path = os.path.join('dongtai_agent_python', 'assess_ext')
c_sources = glob(os.path.join(assess_ext_path, '*.c')) + glob(os.path.join(assess_ext_path, "patch/*.c"))

tempdir = None
funchook_temp = None

include_dirs = [
    os.path.join(assess_ext_path, 'include'),
    os.path.join(assess_ext_path, 'funchook', 'include'),
]

runtime_library_dirs = []
link_args = []
extra_compile_args = []
strict_build_args = []
platform_args = []

if platform.startswith('linux'):
    platform_args = ['-Wno-cast-function-type']
elif platform.startswith('darwin'):
    link_args = ['-rpath', '@loader_path']

if platform == 'win32':
    libraries = ['funchook', 'distorm', 'psapi']
    library_dirs = [
        os.path.join(assess_ext_path, 'funchook', 'build', 'Release'),
    ]
else:
    libraries = ['funchook']
    library_dirs = [
        os.path.join(assess_ext_path, 'funchook', 'build'),
    ]
    runtime_library_dirs = ['$ORIGIN']
    extra_compile_args = [
        '-Wall',
        '-Wextra',
        '-Wno-unused-parameter',
        '-Wmissing-field-initializers',
    ]
    strict_build_args = ['-Werror']


class BuildExt(build_ext):
    def run(self):
        cmake_cmd = '''
        cmake -DCMAKE_BUILD_TYPE=Release ..
        make
        '''
        if platform == 'win32':
            cmake_cmd = '''
            cmake.exe  -DCMAKE_INSTALL_PREFIX=%s ..
            cmake --build . --config Release
            ''' % os.path.join(assess_ext_path, 'funchook')

        build_dir = os.path.join(assess_ext_path, 'funchook/build')
        if ext_clean and os.path.exists(build_dir):
            rmtree(build_dir)
        if not os.path.exists(build_dir):
            os.mkdir(build_dir)

        build_script = '''
        cd %s
        %s
        ''' % (build_dir, cmake_cmd)
        if os.system(build_script) != 0:
            raise DistutilsExecError("Failed to build DongTai-agent-python C extension")

        build_ext.run(self)

        if platform == 'win32':
            return

        global tempdir
        global funchook_temp

        ext = '1.dylib' if platform.startswith('darwin') else 'so.1'
        funchook_name = 'libfunchook.{}'.format(ext)
        funchook = os.path.join(assess_ext_path, 'funchook/build/' + funchook_name)

        tempdir = tempfile.mkdtemp('dongtai-agent-python-libfunchook')
        funchook_temp = os.path.join(tempdir, funchook_name)
        self.copy_file(funchook, funchook_temp)


class InstallLib(install_lib):
    def run(self):
        install_lib.run(self)

        if platform == 'win32':
            return

        global tempdir
        global funchook_temp

        if funchook_temp is not None:
            dest_dir = os.path.join(self.install_dir, assess_ext_path)
            self.copy_file(funchook_temp, dest_dir)
            rmtree(tempdir)


extensions = [
    Extension(
        'dongtai_agent_python.assess_ext.c_api',
        c_sources,
        libraries=libraries,
        include_dirs=include_dirs,
        library_dirs=library_dirs,
        runtime_library_dirs=runtime_library_dirs,
        extra_compile_args=extra_compile_args + strict_build_args + platform_args,
        extra_link_args=link_args,
    )
]


setup(
    name='dongtai_agent_python',
    scripts=['scripts' + os.sep + 'dongtai-cli'],
    include_package_data=True,
    cmdclass=dict(build_ext=BuildExt, install_lib=InstallLib),
    ext_modules=extensions,
    entry_points={
        'console_scripts': ['dongtai-cli = dongtai_agent_python.cli:main'],
    }
)
