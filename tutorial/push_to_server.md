## Pull Request on Server
```
ssh [username]@webwork.cse.ucsd.edu
cd /opt/Webwork_AdaptiveHints
git stash
git pull
git stash apply
bash src/servers/init-scripts/restart_servers.sh
```
