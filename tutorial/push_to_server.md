## Pull Request on Server
```
ssh [username]@webwork.cse.ucsd.edu
cd /opt/Webwork_AdaptiveHints
git stash
github pull
git stash apply
bash src/adaptive-hint-servers/init-scripts/restart_servers.sh
```
