# Automation
A Raspberry Pi automated alarm clock/music server.

Set up your Raspberry Pi in a room, hook it up to some speakers and position the camera so that a large area of the room is visible. When you walk into the room, your Raspberry Pi will tell you how many emails you have and will start playing music.

## Requirements

* Raspberry Pi camera module, connected and enabled
* bottle python module (installable through pip)
* pyttsx python module (installable through pip)
* espeak package (installable through apt-get)
* mplayer package (installable through apt-get)

In main.py make sure to put in your own IMAP credentials so that your email can be checked.

To make the server run at start, make an /etc/init.d/ script. The following link can be helpful: [https://www.debian-administration.org/article/28/Making_scripts_run_at_boot_time_with_Debian](https://www.debian-administration.org/article/28/Making_scripts_run_at_boot_time_with_Debian)

To access your Raspberry Pi through the web and to upload music or set alarms, go to its IP Address at port 8080.
