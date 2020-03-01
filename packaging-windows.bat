pyinstaller -w -y -n vertreader ^
--add-data="vertreader\vertreader.svg;." ^
--add-data="LICENSE.txt;." ^
vertreader\__init__.py

pause