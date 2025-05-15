from setuptools import setup, find_packages

setup(
    name='AiMeRiC',
    version='0.5.1',
    author='Pere Garau',
    description='Anàlisi Informatitzada del Metre i el Ritme del Català',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'spacy',
        'openpyxl',
        'tabulate',
        'tqdm',
        'matplotlib',
        'jupyter',
        'folium',
        'getUSB',
        'colorama',
        'cfonts'
        ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: ©2025, Pere Garau Borràs',
        'Operating System :: Windows',
        ],
    python_requires='>=3.6',
    )
