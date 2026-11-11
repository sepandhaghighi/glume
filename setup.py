# -*- coding: utf-8 -*-
"""Setup module."""
from setuptools import setup


def read_description() -> str:
    """Read README.md and CHANGELOG.md."""
    try:
        with open("README.md") as r:
            description = "\n"
            description += r.read()
        with open("CHANGELOG.md") as c:
            description += "\n"
            description += c.read()
        return description
    except Exception:
        return '''Glume is a lightweight Python tool for packing project files into a structured text representation
        optimized for LLM context windows. It collects readable files from a target directory and combines 
        their contents into a single formatted output, optionally including the directory structure tree.
        Glume supports customizable Jinja2 templates, glob-based ignore patterns, automatic .gitignore integration,
        and file processing statistics. It can be used both as a CLI tool and as an importable Python library.
        '''


setup(
    name='glume',
    packages=['glume'],
    version='0.1',
    description='Glume: A Nano File-to-Text Packer for LLM Context Windows',
    long_description=read_description(),
    long_description_content_type='text/markdown',
    include_package_data=True,
    author='Sepand Haghighi',
    author_email='me@sepand.tech',
    url='https://github.com/sepandhaghighi/glume',
    download_url='https://github.com/sepandhaghighi/glume/tarball/v0.1',
    keywords='glume python llm large-language-models llm-context context-window prompt-engineering prompt-management code-context memor jinja2 cli developer-tools',
    project_urls={
        'Source': 'https://github.com/sepandhaghighi/glume'
    },
    install_requires=['memor>=1.4'],
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'Programming Language :: Python :: 3.15',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Markup',
        'Topic :: Utilities',
        'Topic :: Terminals',
    ],
    license='MIT',
    entry_points={
            'console_scripts': [
                'glume = glume.cli:main',
            ]
    }
)
