
## Amazon Web Services Linux Server Configuration

### Catalog Hosting Name

##### Public IP: 
##### Static IP: 
##### Host Name: 

##### SSH Port 5000

# Helpful Links

    Initial Server Setup with Ubuntu 16.04
    https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-16-04

    How To Deploy a Flask Application on an Ubuntu VPS
    https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps

------------------------------------------------------

# Amazon Lightsail Setup

[Seoul Server]
1. Sign up for a Amazon Web Services Lightsail Account
https://aws.amazon.com/
2. Sign into AWS Console
![Create Instance in AWS](readme_images/Create_Instance.png)
3. Private IP = XXX.XX.XX.XX

   Get the hostname from http://www.hcidata.info/host2ip.cgi

4. Download SSH Keypairs
![Accounts Page](readme_images/accounts_page.png)
5. Add TCP Ports
![Firewall](readme_images/firewall.png)
6. Now we are finished with the Amazon Lightsail Setup! 

# Linux Server Configuration Part I

1. Show all files in Mac OSX by typing `$ killall Finder` in the terminal. 
2. Input in terminal `$ defaults write com.apple.finder AppleShowAllFiles TRUE`. 
3. Locate the hidden .ssh folder in the root of your Mac.
4. Move the downloaded `.pem` file into your `.ssh` folder.
![.pem key to .ssh folder](readme_images/ssh.png)
5. Rename the `.pem` file to `udacity.pem`
6. To make the public key usable and secure, go back to your terminal and input `$ chmod 600 ~/.ssh/udacity.pem`
7. Log into Amazon Lightsail Server with `$ ssh -i ~/.ssh/udacity.pem ubuntu@52.192.199.102`
8. Type `$ sudo su -` to become a root user. 
9. Type  `$ sudo adduser grader` to create a user 'grader' 
10. Enter `grader` UNIX password as `udacity`

11. Create a new file under the sudoers directory: `$ sudo nano /etc/sudoers.d/grader`.
12. Fill that file with `grader ALL=(ALL:ALL) ALL` using nano and save it.
![sudoers](readme_images/sudoers.png)
13. In order to prevent the `$ sudo: unable to resolve host error`, edit the hosts by `$ sudo nano /etc/hosts`, and then add `127.0.1.1 ip-10-20-37-65` under `127.0.1.1:localhost`
14. Run `$ sudo apt-get update`
15. Run `$ sudo apt-get upgrade`
16. Run `$ sudo apt-get install finger`


# Linux Server Configuration Part II
1. Open up a new terminal window. Type `$ ssh-keygen -f ~/.ssh/udacity_key.rsa`
2. Keep a blank password
3. In the new terminal window (the one just opened up with instructions above), input `$ cat ~/.ssh/udacity_key.rsa.pub`
4. Copy the RSA key and save it somewhere private.

# Linux Server Configuration Part III
1. Return to the terminal window that is logged into root. Change directory to `$ cd /home/grader`
2. Create a .ssh directory: `$ mkdir .ssh`. Check directory with `$ ls -al` You should see a .ssh folder.
3. Create a file to store the public key with `$ touch .ssh/authorized_keys`
4. Edit the authorized_keys file `$ nano .ssh/authorized_keys` and paste the RSA key from Part II
5. Change the permission: `$ sudo chmod 700 /home/grader/.ssh` and `$ sudo chmod 644 /home/grader/.ssh/authorized_keys`
6. Change the owner from root to grader: `$ sudo chown -R grader:grader /home/grader/.ssh`
7. Restart the ssh service: `$ sudo service ssh restart`
8. We now need to enforce the key-based authentication: `$ sudo nano /etc/ssh/sshd_config`. Find the `PasswordAuthentication` line and change text after to `no`. After this, restart ssh again: `$ sudo service ssh restart`
9. We now need to change the ssh port from 22 to 2200, as required by Udacity: `$ sudo nano /etc/ssh/sshd_config` Find the Port line and change 22 to 2200. Restart ssh: `$ sudo service ssh restart`
10. Disconnect from the server. Log back through port 2200: `$ ssh -i ~/.ssh/udacity_key.rsa -p 2200 grader@52.192.199.102`
11. Disable ssh login for root user. `$ sudo nano /etc/ssh/sshd_config`. Find the `PermitRootLogin` line and edit to `no`. Restart `ssh $ sudo service ssh restart`

# Linux Server Configuration Part IV
1. Log into the server as grader: `$ ssh -i ~/.ssh/udacity_key.rsa grader@52.192.199.102 -p 2200`
2. Disable ssh login for root user: `$ sudo nano /etc/ssh/sshd_config`. Find the `PermitRootLogin` line and edit to `no`. 
3. Restart ssh `$ sudo service ssh restart`
4. Now we need to configure UFW to fulfill the requirement:

* `$ sudo ufw allow 2200/tcp`
* `$ sudo ufw allow 80/tcp`
* `$ sudo ufw allow 123/udp`
* `$ sudo ufw enable`
5. Exit Terminal and take a break.

# Deploying an Application (be careful on these steps)
1. SSH into machine using `$ ssh -i ~/.ssh/udacity_key.rsa grader@52.192.199.102 -p 2200`
2. `$ sudo apt-get install apache2`
3. `$ sudo apt-get install libapache2-mod-wsgi python-dev`
4. `$ sudo apt-get install git`
5. You should see the apache2 ubuntu default page on web address http://52.192.199.102     [PUBLIC IP]
6. Enable mod_wsgi with the command `$ sudo a2enmod wsgi` and restart Apache using `$ sudo service apache2 restart`

# Creating a directory for the application and make the user `grader` the owner.
1. `$ cd /var/www`
2. `$ sudo mkdir catalog`
3. `$ sudo chown -R grader:grader catalog`
4. `$ cd catalog`
5. Clone the project from Github using `$ git clone [your link] catalog`
6. Create a .wsgi file: `$ sudo nano catalog.wsgi` and add the following into this file:

import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/catalog/")

from catalog import app as application
application.secret_key = 'supersecretkey'

7. Rename your application.py, project.py, or whatever you called it in your catalog application folder to `__init__.py` by `$ mv project.py __init__.py`

# Create Our Virtual Environment
1. Make sure you are in `/var/www/catalog`
2. `$ sudo apt-get install python-virtualenv`
3. `$ sudo virtualenv venv`
4. `$ source venv/bin/activate`
5. `$ sudo chmod -R 777 venv`

This is what your command line should look like: (venv) grader@ip-XXX-XX-X-XXX:/var/www/catalog$ 

# Virtualenv setup
1. While our virtual environment is activated we need to install all packages required for our Flask application. Here are some defaults but you may have more to install.
`$ sudo apt-get install python-pip`
`$ sudo pip install flask`
`$ sudo pip install httplib2 oauth2client sqlalchemy psycopg2`

2. Use the `nano __init__.py` command to change the client_secrets.json line to `/var/www/catalog/catalog/client_secrets.json`
3. Paste in the following:

```
<VirtualHost *:80>
    ServerName 52.192.199.102
    ServerAlias ec2-52-192-199-102.ap-northeast-1.compute.amazonaws.com
    ServerAdmin admin@35.167.27.204
    WSGIDaemonProcess catalog python-path=/var/www/catalog:/var/www/catalog/venv/lib/python2.7/site-packages
    WSGIProcessGroup catalog
    WSGIScriptAlias / /var/www/catalog/catalog.wsgi
    <Directory /var/www/catalog/catalog/>
        Order allow,deny
        Allow from all
    </Directory>
    Alias /static /var/www/catalog/catalog/static
    <Directory /var/www/catalog/catalog/static/>
        Order allow,deny
        Allow from all
    </Directory>
    ErrorLog ${APACHE_LOG_DIR}/error.log
    LogLevel warn
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```

4. Enable to virtual host: `$ sudo a2ensite catalog.conf` and DISABLE the default host `$ a2dissite 000-default.conf`. Otherwise, your site will not load with the hostname

# Database Setup

1. `$ sudo -u postgres -i`
2. `$ psql`
3. `postgres=# CREATE USER catalog WITH PASSWORD catalog;`
ERROR:  syntax error at or near "catalog"



Resource Links:
https://github.com/callforsky/udacity-linux-configuration

