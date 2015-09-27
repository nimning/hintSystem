##### We want to create a branch to work on so that our local changes will not effect the master.

##### 1. Before creating a new branch pull the changes from upstream, your master needs to be up to date.
```
git pull
```

##### 2. Create new branch on your local machine
```
git branch <branch_name>
```
##### 3. Switch to new branch
```
git checkout <branch_name>
```
##### 4. Publish your new branch to github
```
git push origin <branch_name>
```
Now other people can see your branch.

##### 5. Remember to make sure you are in your branch before you make changes locally
```
git branch
```
Will show all branches.
##### 6. Make some changes to your new branch
```
git add files
git commit -m "changes something"
```
##### 7. Push to your branch
```
git push origin <branch_name>
```
##### 8. Now to merge master into your branch
```
git pull origin master
```
Solve conflict if there is any.
##### 9. After you merge master into your branch, test locally to make sure the merged version works in your local server
```
vagrant ssh
bash /vagrant/src/servers/init-scripts/restart_servers.sh
```

##### 10. [Create a pull request](https://help.github.com/articles/creating-a-pull-request/)
* On [GitHub](https://github.com/cse103/Webwork_AdaptiveHints), navigate to the repository from which you'd like to propose changes.

* In the "Branch" menu, choose the branch that contains your commits.

* To the left of the "Branch" menu, click the green ""Compare and Review" button.

* The Compare page will automatically select the base and compare branches.

* On the Compare page, click "Create pull request".

* Type a title and description for your pull request.

* Click Create pull request.

##### 11. Ask Professor Freund, Zhen, or Joe to review the pull request and to merge your branch into master.