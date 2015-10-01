## Reload Vagrant ##
```
vagrant reload
vagrant provision
```
## SSH into VM ##
```
vagrant ssh
```
Now you are inside the vagrant virtual machine, so many commands (such as emacs) will not work.
## Restart Server ##
```
cd /vagrant/src/servers/init-scripts
bash runall.sh
```
