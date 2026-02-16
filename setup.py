"""Package configuration."""

from pathlib import Path

from setuptools import find_packages, setup

LONG_DESCRIPTION = Path("README.rst").read_text()
INSTALL_REQUIRES = [
    "dnspython>=2.0.0",
    "pyyaml>=5.3.1",
    "phabricator>=0.7.0",
    "requests",
]

# Extra dependencies
EXTRAS_REQUIRE = {
    # Test dependencies
    "tests": [
        "bandit>=1.6.2",
        "flake8>=3.8.4",
        "flake8-import-order>=0.18.1",
        "mypy>=0.812",
        "pytest>=6.0.2",
        "pytest-cov>=2.10.1",
        "pytest-xdist>=2.2.0",
        "requests-mock>=1.7.0",
        "ruff",
        "sphinx_rtd_theme>=1.0",
        "sphinx-argparse>=0.2.5",
        "Sphinx>=3.4.3",
        "types-PyYAML",
        "types-requests",
        "types-setuptools",
    ],
    "prospector": [
        "prospector[with_everything]==1.16.1",
        "pytest>=6.0.2",
    ],
}

SETUP_REQUIRES = [
    "pytest-runner>=2.11.1",
    "setuptools_scm>=5.0.1",
]

setup(
    author="Luca Toscano",
    author_email="ltoscano@wikimedia.org",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: BSD",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
    ],
    description="Generic library for common tasks in the WMF production infrastructure",
    entry_points={},
    extras_require=EXTRAS_REQUIRE,
    install_requires=INSTALL_REQUIRES,
    keywords=["wmf", "automation"],
    license="GPLv3+",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/x-rst",
    name="wmflib",
    package_data={"wmflib": ["py.typed"]},
    packages=find_packages(exclude=["*.tests", "*.tests.*"]),
    platforms=["GNU/Linux"],
    python_requires=">=3.9",
    setup_requires=SETUP_REQUIRES,
    use_scm_version=True,
    url="https://github.com/wikimedia/operations-software-pywmflib",
    zip_safe=False,
)
