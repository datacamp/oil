import os

from setuptools import setup
from subprocess import check_call


def common_install():
    here = os.path.dirname(__file__) or '.'
    check_call("./build/dev.sh ast".split(), cwd=here)


common_install()


setup(
    name="osh",
    version="0.1.1",
    packages=["osh", "core", "asdl", "frontend", "pylib", "_devbuild", "_devbuild.gen"],
    install_requires=["typing"],
)
