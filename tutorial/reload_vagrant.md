## Reload Vagrant ##
```
vagrant reload
vagrant provision
```
## Restart Server ##
```
vagrant ssh
```
Now you are inside the vagrant virtual machine, so some many commands (such as emacs) will not work.
```
cd /vagrant/src/servers/init-scripts
bash runall.sh
```
