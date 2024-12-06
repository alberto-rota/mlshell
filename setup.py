from setuptools import setup, find_packages

setup(
    name="shellml",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "numpy==2.1.3",
        "plotext==5.3.2",
        "setuptools==75.1.0",
        "textual==0.89.1",

    ],
    description="A texutal interface for monitoring ML experiments in the terminal",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/alberto-rota/shellml",
    author="Alberto Rota",
    author_email="alberto1.rota@polimi.it",
    license="GPLv3",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
