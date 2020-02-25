msiexec /i "Z:\Survey\Survey Software\AGUK Tools\python-3.4.3.msi" /passive /norestart ADDLOCAL=ALL
C:\Python34\Scripts\pip install virtualenv
C:\Python34\Scripts\pip install --upgrade pip
C:\Python34\Scripts\virtualenv C:\aguktools -p C:\Python34\python.exe
C:\aguktools\Scripts\pip install "Z:\Survey\Survey Software\AGUK Tools\SurveyProcessing-0.2.1.zip"