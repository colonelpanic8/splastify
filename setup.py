from setuptools import setup, find_packages


version = '0.0.0'


setup(
    name="splastify",
    version=version,
    packages=find_packages(exclude=('tests*', 'examples')),
    install_requires=['pylast', 'pyyaml'],
    tests_require=['tox', 'pytest', 'mock', 'vcrpy >= 1.1.4'],
    package_data={'': ['*.md', '*.rst']},
    author="Ivan Malison",
    author_email="ivanmalison@gmail.com",
    description="Generate playlists using last.fm user and tag data.",
    license="MIT",
    keywords=["splastify", "last.fm", "music", "spotify",
              "playlist", "scrobble", "tag"],
    url="https://github.com/IvanMalison/tagify.fm",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities",
    ],
)
