Write-Output ""

uv run pytest --cov --cov-report=term --cov-report=html

If (-Not $?)
{
    Write-Output ""
    exit
}

Write-Output ""
