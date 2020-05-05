import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bindpyrame", 
    version="0.3",
    author="llr-online",
    author_email="lorenzo.bernardi@llr.in2p3.fr",
    description="A module to bind to pyrame in pure python 3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="GPLv3",
    url="https://github.com/llr-online/bindpyrame/tree/master",
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        "Programming Language :: Python :: 3",
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.0',
)
