## Download
- Download Vagrant for your platform -> [Vagrant Download](https://www.vagrantup.com/downloads.html)
	- Vagrant is a tool for setting development environments as Virtual Machines- Download VirtualBox to run the development VM -> [VirtualBox Download](https://www.virtualbox.org/wiki/Downloads)- Download and install Ansible -> [How to install ansible](http://docs.ansible.com/intro_installation.html) 	- If you have pip, do
	```
	pip install ansible
	```
	- Ansible is a tool for provisioning/configuring development environments

## Pull from Github- Create a folder and clone the following in the folder
- Clone Webwork_AdaptiveHints [Github URL](https://github.com/cse103/Webwork_AdaptiveHints)
- Clone Administrative_Code [Github URL](https://github.com/cse103/Administrative_Code)

## Download database:
	scp username@webwork.cse.ucsd.edu:../zzhai/webwork.sql Webwork_AdaptiveHints/local_server`

## Start Vagrant- In the directory Webwork_AdaptiveHints (make sure you get the most current pull), do `vagrant up`
	- This will download a base VM image, install all the necessary dependencies for Webwork and Python stuff,
	  and configure (almost) everything you need for a development environment for the adaptive hints infrastructure	- If the provisioning fails, make note of what failed
	- Email Zhen the error
	- Re-run the provisioning `	vagrant provision`

## Config Development Environment- Replace references to **webwork.cse.ucsd.edu** with **192.168.33.10** in:	- src/clients/teacher_client/js/constants.js	- src/servers/rest_server/scripts/checkanswer.pl	- src/servers/rest_server/scripts/renderPG.pl- Set default database username and password in
	- src/servers/rest_server/webwork_config.py
	- username: webworkWrite
	- password: webwork- Configure and run services by typing `vagrant ssh`
	- cd into directory /vagrant/src/servers/init-scripts	- run `sudo bash deploy.sh`	- run `bash restart-servers.sh`- Restart apache2/nginx	- `sudo service apache2 restart`	- `sudo service nginx restart`- Browse to [http://192.168.33.10/webwork2](http://192.168.33.10/webwork2), see if webwork runs- Browse to [http://192.168.33.10/teacher](http://192.168.33.10/teacher), see if hint client works## Remember, do not push any of the change above to github.