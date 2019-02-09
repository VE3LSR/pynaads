import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pynaads",
    version="0.0.2",
    author="VE3LSR / VE3YCA",
    author_email="projects@ve3lsr.ca",
    description="Python library to monitor Pelmorex's NAADS service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VE3LSR/pynaads",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
