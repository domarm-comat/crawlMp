import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="crawlMp",
    version="0.0.1",
    author="Martin Domaracky",
    author_email="domarm@comat.sk",
    description="Multi Process Crawl toolset",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.comat.sk/domarm/crawlMp",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: English",
        "Intended Audience :: Science/Research",
    ],
    install_requires=[
    ],
    extras_requires={
    },
    python_requires='>=3.7',
)
