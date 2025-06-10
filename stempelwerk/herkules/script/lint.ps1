Write-Output ""

poetry run python -m flake8 --config=".\.flake8" herkules/

If (-Not $?)
{
    exit
}
