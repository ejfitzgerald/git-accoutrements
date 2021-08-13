from os import path

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='git-accoutrements',
    version='0.1.0',

    description='A collection of tools to help with a git based development workflow',
    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://github.com/ejfitzgerald/git-accoutrements',

    author='Ed FitzGerald',
    author_email='ejafitzgerald@gmail.com',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
    ],

    keywords='git workflow development',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.5, <4',
    install_requires=[
        'colored',
        'toml',
    ],

    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },

    entry_points={
        'console_scripts': [
            'git-feature=accoutrements.cmd.feature:main',
            'git-master=accoutrements.cmd.master:main',
            'git-chore=accoutrements.cmd.chore:main',
            'git-tidy=accoutrements.cmd.tidy:main',
            'git-bugfix=accoutrements.cmd.bugfix:main',
            'git-del=accoutrements.cmd.del:main',
            'git-ditto=accoutrements.cmd.ditto:main',
        ],
    },

    project_urls={
        'Bug Reports': 'https://github.com/ejfitzgerald/git-accoutrements/issues',
        'Source': 'https://github.com/ejfitzgerald/git-accoutrements',
    },
)
