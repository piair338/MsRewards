#  MsReward


A Microsoft reward automator, designed to work headless on a raspberry pi. Tested with a pi 3b+ and a pi 4 2Gb .  
Using a discord webhook to log everything.  
Using Selenium and geckodriver.  
You have to fill the config file.  

you have to put your credentials in the same folder as the script, in a  `.csv` file. You have to put login and password this way : 
```
email1,password1
email2,password2
```

You have to put a list with a dictionnary in the same folder as the script, in a   `.txt` file. It should have a lot of words, used to make random search on bing, as shown in the example file.  
Tou can add a link to a website where content is only the link of the monthly fidelity card 
You should limit to 6 account per IP.
![image](https://user-images.githubusercontent.com/74496300/155960737-061229ca-db8c-4e66-9aef-542d9e709bb2.png)
