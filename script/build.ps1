Write-Output ""

uv build --clear

If (-Not $?)
{
    Write-Output ""
    exit
}

Write-Output ""
