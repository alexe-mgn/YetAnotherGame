@echo off
if not exist .gitmodules (
    echo submodules was not init
    echo initializing config
    git submodule init
    echo done
)
echo updating submodules
git submodule update
echo done
pause
