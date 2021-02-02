import setuptools
import phiorm


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


github_url = "https://github.com/rahungria/phiorm"


setuptools.setup(
    name="phiorm",
    packages=['phiorm'],
    version=phiorm.__version__,
    author="Raphael Hungria",
    author_email="rhja93@gmail.com",
    description="simple ORM for personal usage",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=github_url,
    download_url=f'{github_url}/archive/{phiorm.__version__}.tar.gz',
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)
