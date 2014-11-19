@echo off
if (%1)==() goto VersionNotGiven

md previousReleases\%1

if not exist previousReleases\%1 goto FolderNotCreated

md previousReleases\%1\DlgCheck2
if not exist previousReleases\%1 goto FolderTwoNotCreated

copy *.py previousReleases\%1
copy dlgCheck2 previousReleases\%1\DlgCheck2


goto finished

:FolderNotCreated
echo.
echo Could not create the folder "previousReleases\%1"
echo.
goto finished

:FolderTwoNotCreated
echo.
echo Could not create the folder "previousReleases\%1\DlgCheck2"
echo.
goto finished


VersionNotGiven
echo.
echo please specify the version of the backup
echo.
goto finished

:finished
