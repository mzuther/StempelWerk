Write-Output ""
Write-Output "[RUFF]"
Write-Output ""

uv run ruff format
uv run ruff check --fix

If (-Not $?)
{
    Write-Output ""
    exit
}

Write-Output ""
Write-Output "[MYPY]"
Write-Output ""

uv run mypy .

If (-Not $?)
{
    Write-Output ""
    exit
}

Write-Output ""
