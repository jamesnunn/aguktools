from setuptools import setup

with open('requirements.txt') as f:
    reqs = f.read().splitlines()


setup(
    name='aguktools',
    version='0.4.4',
    packages=['aguktools', 'eacsd'],
    install_requires=reqs,
    entry_points={
        'console_scripts': [
            'textreplace = aguktools.textreplace:cli_main',
            'renamephotos = aguktools.renamephotos:main',
            'gpscsv = aguktools.gps_csv:cli_main',
            'checkthisisisis = aguktools.checkisis:cli_main',
            'linkechodata = aguktools.link_echo_data:cli_main',
            'eacsderrors = aguktools.eacsderrors:cli_main',
        ],
        'gui_scripts': ['aguktools = aguktools.aguktools:main']
        },
    )
