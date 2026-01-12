Write-Output ""
Write-Output "[QUICK TESTS]"
Write-Output ""

# run quick tests first
uv run pytest --ignore=".\.git" -m "not slow" $args

If (-Not $?)
{
    exit
}

Write-Output ""
Write-Output "[SLOW TESTS]"
Write-Output ""

# run slow tests only when all other tests have passed
uv run pytest --ignore=".\.git" -m "slow" $args

If (-Not $?)
{
    exit
}
