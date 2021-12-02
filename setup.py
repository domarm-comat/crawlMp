import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="crawlMp",
    version="0.1",
    license='MIT',
    author="Martin Domaracký",
    author_email="domarm@comat.sk",
    description="Multi Process Crawl toolset",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.comat.sk/domarm/crawlMp",
    packages=setuptools.find_packages(),
    scripts=['crawlMp/scripts/search_fs_mp'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Intended Audience :: Science/Research",
    ],
    install_requires=[
    ],
    extras_requires={
    },
    python_requires='>=3.7',
)
