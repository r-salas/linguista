import re
import os

from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), "linguista", '__init__.py')) as f:
    init_py = f.read()


with open(os.path.join(os.path.dirname(__file__), 'README.md'), "r") as f:
    long_description = f.read()


def get_property(prop):
    result = re.search(r'{}\s*=\s*[\'"]([^\'"]*)[\'"]'.format(prop), init_py)
    return result.group(1)


setup(
    name='linguista',
    version=get_property("__version__"),
    author=get_property('__author__'),
    author_email="me@rubensalas.ai",
    description=get_property("__description__"),
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/r-salas/linguista',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
    setup_requires=[
        "setuptools"
    ],
    install_requires=[
        "Jinja2",
    ],
    extras_require={
        "openai": ["openai>=1.0.0"],
        "anthropic": ["anthropic"],
        "redis": ["redis[hiredis]"],
    }
)
