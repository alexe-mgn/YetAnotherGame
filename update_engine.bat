@echo off

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

pause
