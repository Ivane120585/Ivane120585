from setuptools import setup, find_packages

setup(
    name="scrollwrappedcodex",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    entry_points={
        'console_scripts': [
            'scrollcodex=cli:main',
            'scrollfile=run_scroll_file:main'
        ],
    },
    author="Stanley Osei-Wusu",
    description="A scroll-sealed AI code execution engine powered by Lashon HaScroll.",
    classifiers=["Programming Language :: Python :: 3"],
) 