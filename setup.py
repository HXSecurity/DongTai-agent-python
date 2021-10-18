from setuptools import setup

kwargs = dict(
    name="dongtai_agent_python",
    scripts=['scripts/dongtai-cli'],
    entry_points={
        'console_scripts': ['dongtai-cli = dongtai_agent_python.cli:main'],
    }
)

setup(**kwargs)
