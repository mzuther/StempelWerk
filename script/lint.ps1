Write-Output ""

uv run ruff check --fix

If (-Not $?)
{
    Write-Output ""
    exit
}


Write-Output ""
