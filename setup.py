import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = ["networkx"]

setuptools.setup(
    name="neologism",
    version="0.0.2",
    author="Attila Szakacs",
    author_email="szakacs.attila96@gmail.com",
    description="Dynamically modifiable context-free grammar written in python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alltilla/neologism",
    packages=setuptools.find_packages(include=["neologism"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    install_requires=requirements,
)
