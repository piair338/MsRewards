#  MsReward


A Microsoft reward automator, designed to work headless on a raspberry pi. Tested with a pi 3b+ and a pi 4 2Gb .  
Using a discord webhook or SQL to log points everydays.  
Using Selenium and geckodriver.

## If you're using docker (way easier)  
to use docker, run 
```
sudo docker build .
#copy the build id
docker run -ti --name MsRewards [build id]
```
Then, fill the config and start the programm everydays with 
```
docker start MsRewards
```

## Other configuration

To use the database, I recommand MySql, Create a database with the name you want and create a table `daily`, like the one from the image : 
![B96F2F6D-7257-4F12-BFA7-0BEC3FB72993](https://user-images.githubusercontent.com/74496300/172872979-05396b6b-b682-471a-b71b-41602d816504.jpeg)

You have to use the default worldlist (`sudo apt install wfrench`). The language is french by default, but you can change it if you want.  
You can add a link to a website where content is only the link of the monthly fidelity card.  

  
You should limit to 6 account per IP, and DON'T USE outlook account, they are banned.
![image](https://user-images.githubusercontent.com/74496300/155960737-061229ca-db8c-4e66-9aef-542d9e709bb2.png)

## if you're **not** using docker 
You have to **fill the config file**.  

you have to put your credentials in the same folder as the script, in a  `.csv` file. You have to put login and password this way : 
```
email1,password1
email2,password2
```
