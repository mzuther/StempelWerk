Write-Output ""

uv run flake8 --config=".flake8" src/stempelwerk/

If (-Not $?)
{
    exit
}
