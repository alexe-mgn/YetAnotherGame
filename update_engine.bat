@echo off
if not exist Engine\update_engine.bat (
echo initializing config
git submodule init
echo --done

echo fetching
git fetch
echo --done

echo updating submodules
git submodule update
echo --done

echo performing pull from remote
git submodule foreach git pull
echo --done

echo If something doesn't function correctly go to ./Engine and run (This script is WIP i guess)
echo git fetch
echo git checkout master
echo git pull
echo Engine directory is separate repository you can work with
) else (
cd Engine
call update_engine.bat & exit
)
