# StarCraft II Coop Overlay (SCO)

This app looks for recent replays from StarCraft II Co-op, parses them and shows the information as overlay onscreen. Or it can be added as another layer in Open Broadcaster Software (OBS) or other streaming software applications.

The overlay is fully customizable through simple editing of the HTML file. Its style can be changed, new functions or elements can be added to the visible overlay (images, text, etc).

![Screenshot](/Screenshots/scr1.jpg)

# 
Download links: 
* [Mega](https://mega.nz/file/QpFjDSRJ#DvHCKvK4gI72JoVwTfhI2p2VeL-CAymNnkhY0QJ-WpU)
* [Google-drive](https://drive.google.com/file/d/11Jgk8qFB0x0RAWNoYhKd08nH0U7wlQMC/view?usp=sharing)
* Or run the script with Python

# How to use
1. Extract the archive
2. Run the executable
3. The app will show in the system tray after few seconds
4. Play StarCraft II Co-op

![system tray](/Screenshots/systray1.png)

* If you want it add it as overlay in OBS separatedly, add the HTML to your sources in OBS, and set its width and height to your screen resolution.


# Config file
**Changes take effect the next time you start the app!**

You don't need to change anything in the config file for normal usage.

* **Changing hotkeys for manual overlay display**

  KEY_SHOW = Ctrl+/
  
  KEY_HIDE = Ctrl+

* **Choosing players that will be preferably shown on top**

  PLAYER_NAMES = Maguro,SeaMaguro
  
* **Changing the duration for how long the overlay is visible when shown automatically (in seconds)**
  
  DURATION = 30
  
* **Hiding overlay. This can be useful if you only want the overlay to be shown in OBS or browser**  

  SHOWOVERLAY = False
  
* **If you want to change the folder where it looks for replays. But it should fine them alone.**

  ACCOUNTDIR = C:\Users\Maguro\Documents\StarCraft II\Accounts
  
* **Other for debugging purposes**

How old replays it looks for (in seconds).

REPLAYTIME = 60

Enables logging.

LOGGING = True


# Other notes
* It works with both borderless and fullscreen mode in StarCraft II.
* I haven't tested it with non-English versions of the game.
* You can edit the layout .html file. Changing its style through CSS or other formatting with javascript.
* [sc2reader](https://github.com/ggtracker/sc2reader) was used as replay parser.
