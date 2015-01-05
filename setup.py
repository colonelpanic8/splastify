from setuptools import setup, find_packages


version = '0.0.0'


setup(
    name="tagify.fm",
    version=version,
    packages=find_packages(exclude=('tests*', 'examples')),
    install_requires=['requests >= 2.4.1', 'simplejson', 'six >= 1.8.0', 'pylast'],
    tests_require=['tox', 'pytest', 'mock', 'contextlib2', 'vcrpy >= 1.1.2'],
    package_data={'': ['*.md', '*.rst']},
    author="Ivan Malison",
    author_email="ivanmalison@gmail.com",
    description="Generate playlists using last.fm user and tag data.",
    license="MIT",
    keywords=["last.fm", "music", "spotify", "playlist"],
    url="https://github.com/IvanMalison/tagify.fm",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities",
    ],
)
