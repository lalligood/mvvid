from setuptools import setup, find_packages

setup(
    name="mvvid",
    version="2021.05.28",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "mvvid = mvvid.main:main",
        ]
    },
)
