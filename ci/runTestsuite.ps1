# Credits to: 
# https://github.com/originell/jpype/appveyor/runTestsuite.ps1
#

function run {
    Write-Host $env:APPVEYOR_BUILD_FOLDER

    cd $env:APPVEYOR_BUILD_FOLDER

    # Show file extensions
    Set-ItemProperty -LiteralPath "HKCU:Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "HideFileExt" -Value "0" -Force
    Stop-Process -Name Explorer -Force
    Start-Sleep -Seconds 10

    coverage run --source=pywinauto -m unittest discover -s pywinauto/unittests -v
    $success = $?
    Write-Host "result code of tests:" $success

    coverage html -d Coverage_report

    # return exit code of testsuite
    if ( -not $success) {
        throw "testsuite not successful"
    }
}

run
