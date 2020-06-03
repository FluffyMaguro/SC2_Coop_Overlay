# StarCraft II Coop Overlay (SCO)

This app looks for recent replays from StarCraft II Co-op, parses them and shows the information as overlay onscreen. Or it can be added as another layer in Open Broadcaster Software (OBS) or other streaming software applications.

The overlay is fully customizable through simple editing of the HTML file. Its style can be changed, new functions or elements can be added to the visible overlay (images, text, etc).

![Screenshot](/Screenshots/scr1.jpg)

# 
Download links: 
* [Mega](https://mega.nz/file/M51ClYAa#8k0Xgj5yU3GiUTwUZRnf7ssnVvvRwGlrDTPzyI___C0)
* [Google-drive](https://drive.google.com/file/d/1gbsPGCzPZSZlXW88H7wfDZmMwjUZByIS/view)
* Or run the script with Python

# How to use
1. Extract the archive
2. Run the executable
3. The app will show in the system tray after few seconds
4. Set in-game display mode to Windowed fullscreen (borderless)

![system tray](/Screenshots/systray.jpg)

![Screenshot](/Screenshots/Display.jpg)


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
  
* **Hiding overlay. This can be useful if you want the overlay to be shown only in OBS or browser**  

   SHOWOVERLAY = False
  
* **If you want to change the folder where it looks for replays. But it should fine them alone.**

   ACCOUNTDIR = C:\Users\Maguro\Documents\StarCraft II\Accounts
  
* **How old replays it looks for (in seconds).**

   REPLAYTIME = 60

* **Enables logging.**

   LOGGING = True
   
* **Added an option for automactic upload of analysed replays to https://starcraft2coop.com/**

   AOM_NAME = Maguro (account name)

   AOM_SECRETKEY = .... (secret key generated on the site)

# Other notes
* The overlay works with the borderless mode (windowed fullscreen) in StarCraft II. In the fullscreen mode, the overlay often loses focus and won't show over the game. 
* You can edit the layout .html file. Changing its style through CSS or other formatting with javascript.
* [sc2reader](https://github.com/ggtracker/sc2reader) was used as replay parser.

# Change log
* 1.6 Added support for https://starcraft2coop.com & small tweaks

* 1.0 – 1.5 Initial versions
