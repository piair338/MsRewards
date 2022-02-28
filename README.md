#  MsReward


A Microsoft reward automator, designed to work headless on a raspberry pi. Tested with a pi 3b+ and a pi 4 2Gb .  
Using a discord webhook to log everything.  
Using Selenium and geckodriver.  
You have to create a file named config, containing the following :  
```
[DEFAULT]
motpath = # Path to liste.txt file
logpath = # Path to login.csv file
successlink = # Link of the webhook to log success
errorlink =  # Link of the webhook to log errors

embeds = True # Send embeds instead of text
Headless = True # Run Headless
Log = False # Show Logs
```
you have to put your credentials in the same folder as the script, in a file named `login.csv`. You have to put info this way : `email,password`     
you have to put a list with a dictionnary in the same folder as the script, in a file named  `liste.txt`  .It should have a lot of words, used to make random search on bing, as shown in the example file.  

![image](https://user-images.githubusercontent.com/74496300/155960737-061229ca-db8c-4e66-9aef-542d9e709bb2.png)
