pyinstaller -w -y -n vertreader ^
-i vertreader.ico ^
--add-data="vertreader\vertreader.svg;vertreader" ^
--add-data="LICENSE.txt;." ^
vertreader\__init__.py

pause