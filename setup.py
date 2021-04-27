
import re
from setuptools import setup
from setuptools import find_packages


DESCRIPTION = "Play any radio around the globe right from the terminal"


def get_version():
    return "1.0.0"
    # content = open("./radio-active/__init__.py").read()
    # mo = re.search(r"__version__\s+=\s+'([^']+)'", content)
    # if not mo:
    #     raise RuntimeError(
    #             'Unable to find version string in radio-active/__init__.py'
    #         )
    # return mo[1]


def readme():
    with open("README.md") as f:
        return f.read()


def required():
    with open("requirements") as f:
        return f.read().splitlines()


setup(
    name="radio-active",
    version=get_version(),
    description=DESCRIPTION,
    long_description=readme(),
    long_description_content_type="text/markdown",
    keywords="pyradios wrapper radios api shortwave internet-radio cli app",
    author="Dipankar Pal",
    author_email="dipankarpal5050@gmail.com",
    url="https://github.com/deep5050/radio-active",
    license="MIT",
    packages=find_packages(),
    install_requires=required(),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: Console",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: Users",
    ],
    python_requires=">=3.6",
    project_urls={
        "Source": "https://github.com/deep5050/radio-active/",
        "Upstream": "https://api.radio-browser.info/",
    },
)