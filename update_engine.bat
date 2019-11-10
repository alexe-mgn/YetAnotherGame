@echo off

echo initializing config
git submodule init
echo done

echo updating submodules
git submodule update
echo done

pause
