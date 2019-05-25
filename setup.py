from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
from subprocess import check_call, CalledProcessError


def common_install():
    try:
        check_call("./build/dev.sh ast".split())
    except CalledProcessError as c:
        print c


class PostDevelopCommand(develop):
    """Post-installation for installation mode."""

    def run(self):
        common_install()
        develop.run(self)


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        common_install()
        install.run(self)


setup(
    name="osh",
    version="0.0.0",
    packages=["osh", "core", "asdl", "frontend", "pylib", "_devbuild"],
    install_requires=["typing"],
    cmdclass={"develop": PostDevelopCommand, "install": PostInstallCommand},
    include_package_data=True,
)
