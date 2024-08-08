Write-Output ""

# run quick tests first
. "$env:APPDATA\Python\Scripts\poetry.exe" run python -m pytest --ignore=".\.git" -m "not slow" $args

If (-Not $?)
{
    exit
}

Write-Output ""

# run slow tests only when all other tests have passed
. "$env:APPDATA\Python\Scripts\poetry.exe" run python -m pytest --ignore=".\.git" -m "slow" $args

If (-Not $?)
{
    exit
}

. ".\script\lint.ps1"
