Write-Output ""

poetry run python -m flake8 --config=".\.flake8" stempelwerk/

If (-Not $?)
{
    exit
}
