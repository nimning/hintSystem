#Replace references to webwork.cse.ucsd.edu with 192.168.33.10 in:
#  src/clients/teacher_client/js/constants.js
#  src/servers/rest_server/scripts/checkanswer.pl
#  src/servers/rest_server/scripts/renderPG.pl

sed -e 's/webwork.cse.ucsd.edu/192.168.33.10/g' -i .old ../src/clients/teacher_client/js/constants.js
sed -e 's/webwork.cse.ucsd.edu/192.168.33.10/g' -i .old ../src/servers/rest_server/scripts/checkanswer.pl
sed -e 's/webwork.cse.ucsd.edu/192.168.33.10/g' -i .old ../src/servers/rest_server/scripts/renderPG.pl

# Set default database username and password in
#   src/servers/rest_server/webwork_config.py
#   username: webworkWrite
#   password: webwork

sed -e "s/mysql_username = ''/mysql_username = 'webworkWrite'/g" \
    -e "s/mysql_password = ''/mysql_password = 'webwork'/g" \
    -i .old ../src/servers/rest_server/webwork_config.py
