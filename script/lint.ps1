Write-Output ""

uv run flake8 --config=".flake8" stempelwerk/

If (-Not $?)
{
    exit
}
