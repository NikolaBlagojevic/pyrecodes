from setuptools import setup, find_packages

setup(
    name='pyrecodes',
    version='0.3.0',
    author="Nikola Blagojevic and Bozidar Stojadinovic",
    author_email="nikolablagojevicnis@gmail.com",
    description="Software for Regional Recovery Modelling and Resilience Assessment of the Built Environment",
    license="BSD-3-Clause",
    url="https://github.com/NikolaBlagojevic/pyrecodes",
    python_requires=">=3.9",
    packages=find_packages(),
    install_requires=[
        'numpy>=1.24',
        'pandas>=2.0',
        'geopandas>=1.0',
        'shapely>=2.0',
        'matplotlib>=3.7',
        'pyproj>=3.5',
        'contextily>=1.4',
        'Pillow>=10.0',
        'imageio>=2.30',
    ],
    extras_require={
        'household': [
            'openai>=1.0',
            'requests>=2.28',
            'aiohttp>=3.8',
        ],
        'third_party_models': [
            'networkx>=3.0',
            'scipy>=1.10',
            'openpyxl>=3.1',
            'scikit-learn>=1.3',
            'pandana>=0.7',
            'rewet>=0.2.0b12',
            'wntrfr>=1.1.0.1.2',
        ],
    }
)
