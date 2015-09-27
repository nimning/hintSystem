Directories and Files
------------------------------

### Pointers to documentation
* [Documentation in Sphinx](https://readthedocs.org/projects/webwork-adaptivehints/) (figure out how to build after making changes in github)
* [Architecture Diagram](https://docs.google.com/drawings/d/19nmZt2Dzaz0_3F8tUUwOE_SmPAN_-e9J-Xx3GqYPA24/edit) (Update and move to lucidchart which has better templates for block diagrams)

### Structure of this github 
* [**/tutorial**](https://github.com/cse103/Webwork_AdaptiveHints/tree/master/tutorial) ---> Contains tutorial files
	* [**local_config.md**](https://github.com/cse103/Webwork_AdaptiveHints/tree/master/tutorial/local_config.md)
		- tutorial for setting up local development environment
	* [**reload_vagrant.md**](https://github.com/cse103/Webwork_AdaptiveHints/tree/master/tutorial/reload_vagrant.md)
	* [**push_to_server.md**](https://github.com/cse103/Webwork_AdaptiveHints/tree/master/tutorial/push_to_server.md)
		- tutorial for push changes up to the real server
	* [**github_branching.md**](https://github.com/cse103/Webwork_AdaptiveHints/tree/master/tutorial/github_branching.md)
		- tutorial for create and manage github branch
* [**/local_server**](https://github.com/cse103/Webwork_AdaptiveHints/tree/master/local_server) ---> Contains files to setup development environment
	* [**/ansible**](https://github.com/cse103/Webwork_AdaptiveHints/tree/master/ansible)
		- a tool for provisioning/configuring local development environments
	* **CSE103_Fall14.tar.bz2**
		- database files for local development testing
	* **webwork.sql**
		- database dump, used to restore database in local development environments
	* **requirements.txt**
		- used for configuring python dependencies for local development environments
	* **default**
		- used to replace a configuration file in local development environments
* [**/docs**](https://github.com/cse103/Webwork_AdaptiveHints/tree/master/docs) ---> Contains files to generate documentation
* [**/src**](https://github.com/cse103/Webwork_AdaptiveHints/tree/master/src) ---> All of the cod, contains a README.md inside folder
* [**/old**](https://github.com/cse103/Webwork_AdaptiveHints/tree/master/old) ---> Contains old codes
* **Vagrantfile**
	* Used to build the local development environments in current directory
