# raspbery_pi_down_detector
A tool designed to detect how often my Virgin Media internet goes down using a RPi0

This project taught me a lot about databases, flask and building javascript applications and was done primarily as a learning exercise (and also because virgin 
media are overcharging me for their crappy service) so if you see another version of this done elsewhere use theirs since its probably slicker, faster and 
better written. That said if you do want to use this then here is a step by step guide:-

1. Get a raspberry pi zero and a wifi card (or just the raspberry pi if you have a RPi0W).

2. Flash a SD card using raspbian, found here: https://www.raspberrypi.org/downloads/. If this is the first time you've set up a RPi you'll need to flash
the SD card. This isn't a simple copy paste job (as I found out to my frustration the first time I tried owing to my lazyness when it comes to reading docs)
Use the recomended tool, etcher, found here: https://www.balena.io/etcher/

3. Set up the raspberry pi in headless mode. The instructions can be found here: https://howtoraspberrypi.com/how-to-raspberry-pi-headless-setup/. The short version
is that you need to add your wifi network name and password to /etc/wpa_supplicant.conf and since ssh should be auto enabled you should be able to tunnel in. The ip
address will change with every boot however so you will need to give you RPi a static IP by editing /etc/dhcpcd.conf. This file has been predesigned to help you 
but I still recommend looking up a beginners tutorial online. You'll have to click around to find one that's right for you

4. Install git on your RPi using ``sudo apt-get install git``

5. Create a folder **/programs** in your home directory for pi

6. Go to /home/pi/programs and git clone this repo

7. Install mySQL using ``sudo apt-get install mysql-server``

8. Go into mySQL and create a database "pingstore" and set up a user "down" 
with password "virgin" on "localhost". Generic instructions can be found here:
http://recipes.item.ntnu.no/setting-up-an-sql-database-on-the-raspberry-pi/

9. In your new database set up a new table called "storedpings" which has the
columns:

* time - DATETIME
* event - TINYTEXT
* sent_pings - TINYINT(2)
* sent_pings - TINYINT(2)
* receved_pings - TINYINT(2)
* lost_pings - TINYINT(2)
* min_ping_time - FLOAT
* max_ping_time - FLOAT
* avg_ping_time - FLOAT

10. Try and run main.py using the command line using the command

``sudo /usr/bin/python3 /home/pi/programs/raspberry_pi_down_detector.py``

if this doesn't work nothing else will so you need to debug that first. You should be able to look at the first results by going to

``http://<RPi's ip address>:5000/``

11. Now you need to run your server on startup so run ``sudo nano /etc/rc.local`` and add ``/usr/bin/python3 /home/pi/programs/raspberry_pi_down_detector.py`` to this
file after fi but before exit 0. Reboot your RPi using ``sudo reboot now`` and if in 5 minutes you can still access the webpage you've been successful. This step
caused me a great deal of grief so make sure you can run the code not on startup using ``/usr/bin/python3`` before attempting this step.

**Q&A**

Q. Should I use this code?

A. Use it as a reference for how someone else solved the problem but I'm sure there are better versions of this elsewhere. Feel free to use it as you like but
if you start passing it around please send people here

Q. It won't run on startup

A. Try running the script using ``/usr/bin/python3`` first. It's usually a problem with paths

Q. Who's work have you pinched?

A. To do this I have used Flask, chartjs and momentjs.

Q. Why do I need to be online to check if my internet is online?

A. I use chartjs and momentjs which I did not want to package in a github repo. You can download them yourself and mount them to *show_time_lines.html* in the 
templates folder if you want to use this tool offline
