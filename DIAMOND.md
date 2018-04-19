# Special Instructions for Diamond Testing:

## How to Install
1. Install VirtualBox and Vagrant 
	- [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
	- [Vagrant](https://www.vagrantup.com/)
2. Download Ken's vagrantMarch2018 folder. 
3. Open up the "Terminal" in your Mac
4. type `cd ` and drag and drop the vagrantMarch2018 folder into the Terminal program
5. Press enter
6. type `vagrant up` (initial setup should take about 7 minutes because you're buildling a virtual 
computer on mac, therefore, no code can interact with your MAC OSX)
7. type `vagrant ssh`
8. type `cd /vagrant` as instructed in terminal
9. type `python database_setup.py`
10. type `python database_init.py`
10. type `python database login_decorator.py`
11. type `python app.py`

Open up Google Chrome and select File, `New Incognito Window`
12. Access the application locally using http://localhost:5000

Test away. 

If you want to clear the database, just erase the taipeihairsalons.db and start all over again. 

LMK how it looks. I tried my best Diamond Wang/Chen???. =)