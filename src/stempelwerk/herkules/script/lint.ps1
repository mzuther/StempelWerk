Write-Output ""

uv run flake8 --config=".flake8" herkules/

If (-Not $?)
{
    exit
}
