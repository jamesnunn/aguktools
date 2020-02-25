# AGUKTools
A set of processing tools to streamline and standardise file conversion between
various software packages.

## Requirements
These tools require Python 3.4.x.

## Installation
A batch script is provided for installation which supports installation for
Windows only and is currently written to expect specific server locations to exist.
Essentially:

```batch
:: Check for Python Installation
python --version 2>NUL
if ERRORLEVEL 1 GOTO NOPYTHON
goto :HASPYTHON

:NOPYTHON
msiexec /i "Z:\Survey\Survey Software\AGUK Tools\python-3.4.3.msi" /passive /norestart ADDLOCAL=ALL

:HASPYTHON
C:\Python34\Scripts\pip install virtualenv
C:\Python34\Scripts\pip install --upgrade pip
rmdir C:\aguktools /s /Q
C:\Python34\Scripts\virtualenv C:\aguktools -p C:\Python34\python.exe
C:\aguktools\Scripts\pip install "aguktools" --upgrade --find-links "Z:\Survey\Survey Software\AGUK Tools"
```

## Run tests
This requires `pytest` to be installed:

```
pip install pytest
```

Then run from the `aguktools` directory:

```
pytest
```

