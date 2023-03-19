#  MsReward


A Microsoft reward automator, designed to work headless on any server.  
Using a discord webhook or SQL to log points everyday.  
Using Selenium and geckodriver.

## If you're using docker (way easier)  
to use docker, run 
```
sudo docker build .
#copy the build id
sudo docker run -ti --name MsRewards [build id]
```
Then, fill the config and start the programm everydays with 
```
sudo docker start MsRewards
```

## Other configuration

To use the database, I recommand MySql, Create a database with the name you want and create a table `daily`, like the one from the image : 
![B96F2F6D-7257-4F12-BFA7-0BEC3FB72993](https://user-images.githubusercontent.com/74496300/172872979-05396b6b-b682-471a-b71b-41602d816504.jpeg)

You have to use the default worldlist (`sudo apt install wfrench`). The language is french by default, but you can change it if you want.  
You can add a link to a website where content is only the link of the monthly fidelity card.  

  
You should limit to 6 account per IP, and DON'T USE outlook account, they are banned.
![image](https://user-images.githubusercontent.com/74496300/155960737-061229ca-db8c-4e66-9aef-542d9e709bb2.png)

## If you're **not** using docker 

installation recommandation :
```
sudo apt-get install xdg-utils libdbus-glib-1-2 bzip2 wfrench -y

curl -sSLO https://download-installer.cdn.mozilla.net/pub/firefox/releases/91.9.1esr/linux-x86_64/en-US/firefox-91.9.1esr.tar.bz2
tar -xjf firefox-91.9.1esr.tar.bz2
sudo mv firefox /opt/
sudo ln -s /opt/firefox/firefox /usr/bin/firefox


curl -sSLO https://github.com/mozilla/geckodriver/releases/download/v0.31.0/geckodriver-v0.31.0-linux64.tar.gz
tar zxf geckodriver-v0.31.0-linux64.tar.gz
sudo mv geckodriver /usr/bin/

rm geckodriver-v0.31.0-linux64.tar.gz
rm firefox-91.9.1esr.tar.bz2
```
