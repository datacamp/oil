from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
from subprocess import check_call

class PostDevelopCommand(develop):
    """Post-installation for installation mode."""
    def run(self):
        check_call("./build/dev.sh all".split())
        develop.run(self)

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        check_call("./build/dev.sh all".split())
        install.run(self)

setup(
	name = 'osh',
	version = '0.0.0',
	packages = ['osh', 'core', 'oil', 'opy', 'asdl'],
        cmdclass = {
            'develop': PostDevelopCommand, 
            'install': PostInstallCommand
            },
        include_package_data = True)
