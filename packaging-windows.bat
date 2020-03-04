pyinstaller -w -y -n vertreader ^
-i vertreader.ico ^
--add-data="vertreader\vertreader.svg;vertreader" ^
--add-data="vertreader\language\*;language" ^
--add-data="LICENSE.txt;." ^
--add-data="vertreader\ebooklib\LICENSE.txt;ebooklib" ^
vertreader\__init__.py

pause