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

if platform.startswith('darwin'):
    link_args = ['-rpath', '@loader_path']
    platform_args = []
else:
    platform_args = ['-Wno-cast-function-type']
    link_args = []

strict_build_args = ['-Werror']


extensions = [
    Extension(
        'dongtai_agent_python.assess_ext.c_api',
        c_sources,
        libraries=["funchook"],
        include_dirs=[
            os.path.join(assess_ext_path, 'include'),
            os.path.join(assess_ext_path, 'funchook/include'),
        ],
        library_dirs=[os.path.join(assess_ext_path, 'funchook/build')],
        runtime_library_dirs=['$ORIGIN'],
        extra_compile_args=[
            '-Wall',
            '-Wextra',
            '-Wno-unused-parameter',
            '-Wmissing-field-initializers',
        ]
        + strict_build_args
        + platform_args,
        extra_link_args=link_args,
    )
]


tempdir = None
funchook_temp = None


class BuildExt(build_ext):
    def run(self):
        build_script = '''
        cd %s
        mkdir -p build
        cd build
        %s
        cmake -DCMAKE_BUILD_TYPE=Release ..
        make
        ''' % (
            os.path.join(assess_ext_path, 'funchook'),
            'make clean' if ext_clean else '',
        )
        if os.system(build_script) != 0:
            raise DistutilsExecError("Failed to build DongTai-agent-python C extension")

        build_ext.run(self)

        global tempdir
        global funchook_temp

        ext = 'dylib' if platform.startswith('darwin') else 'so.1'
        funchook_name = 'libfunchook.{}'.format(ext)
        funchook = os.path.join(assess_ext_path, 'funchook/build/' + funchook_name)

        tempdir = tempfile.mkdtemp('dongtai-agent-python-libfunchook')
        funchook_temp = os.path.join(tempdir, funchook_name)
        self.copy_file(funchook, funchook_temp)


class InstallLib(install_lib):
    def run(self):
        install_lib.run(self)

        if funchook_temp is not None:
            dest_dir = os.path.join(self.install_dir, assess_ext_path)
            self.copy_file(funchook_temp, dest_dir)
            rmtree(tempdir)


setup(
    name='dongtai_agent_python',
    scripts=['scripts/dongtai-cli'],
    cmdclass=dict(build_ext=BuildExt, install_lib=InstallLib),
    ext_modules=extensions,
    entry_points={
        'console_scripts': ['dongtai-cli = dongtai_agent_python.cli:main'],
    }
)
