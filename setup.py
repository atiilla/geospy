from setuptools import setup, find_packages

setup(
    name='geospyer',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    entry_points={
    'console_scripts': [
        'geospy=cli:main',  # Replace 'cli' with the actual name of your script
    ],
},
    author='Atiilla',
    description='AI powered geo-location to uncover the location of photos.',
    url='https://github.com/atiilla/geospy',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
