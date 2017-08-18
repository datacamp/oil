from setuptools import setup
from setuptools.command.develop import develop
from subprocess import check_call

class PostDevelopCommand(develop):
    """Post-installation for installation mode."""
    def run(self):
        check_call("./build/dev.sh all".split())
        develop.run(self)

setup(
	name = 'osh',
	version = '0.0.0',
	packages = ['osh'],
        cmdclass = { 'develop': PostDevelopCommand },
        include_package_data = True)
