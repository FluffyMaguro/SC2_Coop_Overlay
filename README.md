# SC2 Coop overlay

//image

//video

This app looks for recent replays from StarCraft II Co-op, parses them and shows the information as overlay onscreen. Or it can be added as another layer in Open Broadcaster Software (OBS) or other streaming software applications.

# 
Download executable: [Google-drive]()

# Config file
* You don't need to change anything in the config file for normal usage.
* If you don't want to see overlay on your screen, you can disable it. You might be using it only as OBS overlay.

  SHOWOVERLAY = False 
  
* If you want your name to be always on the top, list your in-game player names in the config file. For example:

  PLAYER_NAMES = Maguro,SeaMaguro

* If the app won't find your replays correctly, you can set the folder path manually. All file and subfolders will be searched for new replays. For example:

  ACCOUNTDIR = C:\Users\Maguro\Documents\StarCraft II\Accounts

# Other notes
* You can use it as an overlay in OBS. Drag the HTML file over the scene and set dimensions to the maximum.
* You can edit the layout .html file. Changing its style through CSS or other formatting with javascript.
* Used StarCraft II replay parser: [sc2reader](https://github.com/ggtracker/sc2reader)
