import os
import sys

from setuptools import find_packages, setup

PY_VER = sys.version_info

if PY_VER < (3, 8):
    raise RuntimeError("fly doesn't support Python version prior 3.8")


def read_version():
    version_file = os.path.join(os.path.dirname(__file__), "fly", "VERSION")
    with open(version_file) as f:
        return f.read()


def read(file_name):
    with open(
        os.path.join(os.path.dirname(__file__), file_name), mode="r", encoding="utf-8"
    ) as f:
        return f.read()


setup(
    name="fly",
    version=read_version(),
    author="beyond-heshipeng",
    description="A highly distributed crawling framework based on asyncio",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author_email="heshipeng777@gmail.com",
    python_requires=">=3.8",
    install_requires=["aiohttp>=3.7.4", "w3lib", "rich"],
    packages=find_packages(),
    license="Apache",
    classifiers=[
        "Framework :: AsyncIO",
        "Intended Audience :: Developers",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: BSD",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    project_urls={
        "Source": "https://github.com/beyond-heshipeng/fly",
    },
    extras_require={"uvloop": ["uvloop"]},
)
