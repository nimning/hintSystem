## Reload Vagrant ##
```
vagrant reload
vagrant provision
```
## Restart Server ##
```
vagrant ssh
# Now you are inside the vagrant virtual machine
cd /vagrant/src/servers/init-scripts
bash runall.sh
```
