import setuptools
from pathlib import Path

ROOT_DIR = Path(__file__).parent.resolve()

long_description = Path(ROOT_DIR, "README.md").read_text()
version = Path(ROOT_DIR, "VERSION").read_text()
requirements = ["networkx"]

setuptools.setup(
    name="neologism",
    version=version,
    author="Attila Szakacs",
    author_email="szakacs.attila96@gmail.com",
    description="Dynamically modifiable context-free grammar written in python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alltilla/neologism",
    project_urls={
        "Bug Tracker": "https://github.com/alltilla/neologism/issues",
        "Documentation": "https://neologism.readthedocs.io/",
    },
    packages=setuptools.find_packages(include=["neologism"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    install_requires=requirements,
)
