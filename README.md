# Automation
A Raspberry Pi automated alarm clock/music server.

RUN AT YOUR OWN RISK. This commit is pretty buggy. If you want a more stable release check out [this commit](https://github.com/jextrevor/Automation/commit/97a6b731f8734e6da3231d26f437e452f653cf7e)

Set up your Raspberry Pi in a room, hook it up to some speakers and position the camera so that a large area of the room is visible. When you walk into the room, your Raspberry Pi will tell you how many unread emails you have (if any) and will start playing music. You can also set alarms and reminders.

## Requirements

* Raspberry Pi camera module, connected and enabled
* bottle python module (installable through pip)
* pyttsx python module (installable through pip)
* espeak package (installable through apt-get)
* mplayer package (installable through apt-get)
* python-wapi package (installable through apt-get)

## Features
* Email checking
* Weather forecast (along with alarms)
* Reminders
* Alarms
* Quiet hours (from 9:00 PM to 6:00 AM)
* Ability to upload music

In main.py make sure to put in your own IMAP credentials so that your email can be checked.

To make the server run at start, make an /etc/init.d/ script. The following link can be helpful: [https://www.debian-administration.org/article/28/Making_scripts_run_at_boot_time_with_Debian](https://www.debian-administration.org/article/28/Making_scripts_run_at_boot_time_with_Debian)

If you're using WIFI, make sure that it's not on power saving mode. The following link can be helpful: [https://learn.adafruit.com/adafruits-raspberry-pi-lesson-3-network-setup/test-and-configure#fixing-wifi-dropout-issues](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-3-network-setup/test-and-configure#fixing-wifi-dropout-issues)

To access your Raspberry Pi through the web and to upload music or set alarms, go to its IP Address at port 8080.

**IMPORTANT: If you have a Model B+ or Pi 2, you *NEED* to change the CAMLED number in main.py to 32**
