Write-Output ""

# install and upgrade poetry
pipx install poetry
pipx upgrade poetry

Write-Output ""
Write-Output "------------------------------------------------------------------------"
Write-Output ""

# create virtual environment
poetry env use python3
poetry env info

Write-Output ""
Write-Output "------------------------------------------------------------------------"
Write-Output ""

# install dependencies
poetry sync --no-root --with dev
Write-Output ""
