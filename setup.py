from setuptools import setup, find_packages

setup(
    name="hpctools",
    version="0.1.0",
    description="A collection of magic tools for everyday high performance computing",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="zabealbe",
    url="https://github.com/zabealbe/hpctools",
    license="GNU General Public License v3 (GPLv3)",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    package_data={
        "hpctools": ["templates/launch_scripts/*.j2"],
    },
    install_requires=["paramiko", "jinja2"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: Other Environment",
    ],
    python_requires=">=3.8",
)
