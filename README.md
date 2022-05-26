#  MsReward


A Microsoft reward automator, designed to work headless on a raspberry pi. Tested with a pi 3b+ and a pi 4 2Gb .  
Using a discord webhook or SQL to log points everydays.  
Using Selenium and geckodriver.

You have to **fill the config file**.  

you have to put your credentials in the same folder as the script, in a  `.csv` file. You have to put login and password this way : 
```
email1,password1
email2,password2
```

You have to use the default worldlist (`sudo apt install wfrench`). The language is french by default, but you can change it if you want. 
You can add a link to a website where content is only the link of the monthly fidelity card.
You should limit to 6 account per IP, and DON'T USE outlook account, they are banned.
![image](https://user-images.githubusercontent.com/74496300/155960737-061229ca-db8c-4e66-9aef-542d9e709bb2.png)
