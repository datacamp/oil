from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
from subprocess import check_output, CalledProcessError


def common_install():
    print(check_output("echo $PWD && ls && ./build/dev.sh ast".split()))


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
    packages=["osh", "core", "opy", "asdl"],
    install_requires=["typing"],
    cmdclass={"develop": PostDevelopCommand, "install": PostInstallCommand},
    include_package_data=True,
)
