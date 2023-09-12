from setuptools import find_packages
from setuptools import setup

from radioactive.app import App
import io

app = App()

DESCRIPTION = "Play any radio around the globe right from the terminal"
VERSION = app.get_version()


def readme():
    with io.open("README.md", "r", encoding="utf-8") as f:
        return f.read()


def required(sfx=''):
    with io.open(f"requirements{sfx}.txt",encoding="utf-8") as f:
        return f.read().splitlines()


setup(
    name="radio-active",
    version=VERSION,
    description=DESCRIPTION,
    long_description=readme(),
    long_description_content_type="text/markdown",
    keywords="pyradios wrapper radios api shortwave internet-radio cli app",
    author="Dipankar Pal",
    author_email="dipankarpal5050@gmail.com",
    url="https://github.com/deep5050/radio-active",
    license="MIT",
    entry_points={
        "console_scripts": [
            "radioactive = radioactive.__main__:main",
            "radio = radioactive.__main__:main",
        ]
    },
    packages=find_packages(exclude=["test*"]),
    install_requires=required(),
    extras_require={'dev': required('-dev')},
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio",
    ],
    python_requires=">=3.6",
    project_urls={
        "Source": "https://github.com/deep5050/radio-active/",
        "Upstream": "https://api.radio-browser.info/",
    },
)