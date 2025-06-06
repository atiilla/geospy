from setuptools import setup, find_packages
import os

# Read the README file for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='geospyer',
    version='0.1.9',
    packages=find_packages(),
    install_requires=[
        'requests>=2.31.0,<3.0.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0',
            'safety>=2.0.0',
            'pip-audit>=2.0.0',
        ],
        'test': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'geospyer=geospyer.cli:main',
        ],
    },
    author='Atiilla',
    author_email='',
    description='AI powered geo-location to uncover the location of photos.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/atiilla/geospy',
    project_urls={
        'Bug Reports': 'https://github.com/atiilla/geospy/issues',
        'Source': 'https://github.com/atiilla/geospy',
        'Documentation': 'https://github.com/atiilla/geospy#readme',
    },
    keywords=['geolocation', 'ai', 'photos', 'computer-vision', 'gemini'],
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Image Recognition',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
        'Environment :: Console',
        'Natural Language :: English',
    ],
)
