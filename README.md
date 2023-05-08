#  MsReward


A Microsoft reward automator, designed to work headless on any x64 server.  
Using a discord webhook or SQL to log points everyday.  
Using Selenium and Geckodriver.
# Installation instruction
Make sure your contry is [supported by MS Rewards](https://support.microsoft.com/en-us/topic/microsoft-rewards-regions-9795ec47-c0f4-a33e-aede-738903359d63).  
Create 5 Microsoft accounts, that the programm will use.    
- [linux](#linux)
- [Windows](#windows)
- [MacOS](#macos)
- [Database configuration](#database)
- [Options](#options)
- [Flags](#flags)   
## Linux

### Using docker (Recommended)  
Make sure that [docker](https://docs.docker.com/get-docker/) and [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) are installed.  
Clone the repository:
```
git clone https://github.com/piair338/MsRewards
```
Build the docker container:
```
cd MsRewards
sudo docker build -t msrewards .
```
Run the app for the first time to configure it.  
```
sudo docker run -ti --name MsRewards msrewards
```
Then to run it everyday, you can use cron and add the line: 
```
10 10 * * * sudo docker start MsRewards
```

### **not** using docker (not recommended) 
**This is only a recommandation and shouldn't be used !**
```
sudo apt-get install xdg-utils libdbus-glib-1-2 bzip2 wfrench tigervnc-standalone-server xvnc -y

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
## Windows
Not yet tested, but using docker should work.  
## MacOS
I don't have a mac (yet) so i can't test, but again, install docker and follow the linux installation.  

# Database

To use the database, I recommend MySql, Create a database with the name `MsRewards` and create a table `daily`, like the one from the image : 
![B96F2F6D-7257-4F12-BFA7-0BEC3FB72993](https://user-images.githubusercontent.com/74496300/172872979-05396b6b-b682-471a-b71b-41602d816504.jpeg)

# Options 
TODO  
# Flags
## Override
Enable you to choose what action to perform on which account. **Linux only**
```
python3 main.py -o
```
## VNC
Enble a vnc to a specific port
```
python3 main.py -v 1234
```
## config
Tell the programm which config to use.  
Default to ./user_data/config.cfg  
Putting only a number is equivalent to ./user_data/config[number].cfg 
```
python3 main.py -c 12
```
## Add points to database
Add points to the database using the credentials provided in the default config file.  
argument : file with a list of `account,points`
```
python3 main.py -a file.csv
```


