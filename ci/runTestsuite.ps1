# Credits to: 
# https://github.com/originell/jpype/appveyor/runTestsuite.ps1
#
function upload($file) {
    trap [Exception]
    {
        Write-Output $_.Exception
    }
    Write-Output "Uploading: $file"

    $wc = New-Object 'System.Net.WebClient'
    $wc.UploadFile("https://ci.appveyor.com/api/testresults/junit/$($env:APPVEYOR_JOB_ID)", $file)

    $test_report_dir = ".\TestResultsReport"
    md -Force $test_report_dir | Out-Null
    $revid = $($env:APPVEYOR_REPO_COMMIT).Substring(0, 8)
    $rep_dest = "$test_report_dir\$($env:APPVEYOR_JOB_ID)-$revid-$($env:PYTHON_VERSION)-$($env:PYTHON_ARCH)-UIA$($env:UIA_SUPPORT)-result.xml"

    Write-Output "Copying test report to: $rep_dest"
    cp $file $rep_dest
    Push-AppveyorArtifact $rep_dest
}

function run {
    Write-Output $env:APPVEYOR_BUILD_FOLDER

    cd $env:APPVEYOR_BUILD_FOLDER

    if ($env:APPVEYOR_BUILD_WORKER_IMAGE -match "Visual Studio 2019") {
        # Show file extensions
        Set-ItemProperty -LiteralPath "HKCU:Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "HideFileExt" -Value "0" -Force
        Stop-Process -Name Explorer -Force
        Start-Sleep -Seconds 10
    }

    $faulthandler_opt = "-p no:faulthandler"
    if ($env:PYTHON_VERSION -match "2.7" -or $env:PYTHON_VERSION -match "3.5" -or $env:PYTHON_VERSION -match "3.6") {
        $faulthandler_opt = ""
    }

    $results = "results.xml"
    $ignored = "--ignore=testall.py" # " --ignore=test_application_linux.py --ignore-glob=test_*atspi*.py"
    pytest --junit-xml=$results --tb=native --capture=no --show-capture=stdout $faulthandler_opt -v --verbosity=3 --cache-clear --durations=15 $ignored --log-level=DEBUG --cov-report html:Coverage_report --cov=pywinauto pywinauto\unittests\test_uiawrapper.py
    $success = $?
    Write-Output "result code of pytest: $success"

    upload $results

    # return exit code of testsuite
    if ( -not $success) {
        throw "testsuite not successful"
    }
}

run
