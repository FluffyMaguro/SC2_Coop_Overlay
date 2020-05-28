# SC2 Coop overlay

//image
//video

This app looks for recent replays from StarCraft II Co-op, parses them and shows the information as overlay onscreen. Or it can be added to OBS or other streaming software applications.

# 
Download executable: [Google-drive]()

# Config file
* You don't need to change anything in the config file for normal usage.
* If you don't want to see overlay on your screen, for example when you are using it for OBS only.

  SHOWOVERLAY = False 
  
* If you want your name to be always on top, set your in-game player names in config file, e.g.

  PLAYER_NAMES = Maguro,SeaMaguro

* If the app  won't find your replays correctly, you can set the path manually. All file and subfolders will be searched for new replays. E.g.

  ACCOUNTDIR = C:\Users\Maguro\Documents\StarCraft II\Accounts

# Other notes
* You can use the overlay in OBS. Just drag it over the scene and set dimensions to max.
* You can edit the layout .html file. Changing its style through CSS or other formatting with javascript.

# 
Current version: 1

Used StarCraft II replay parser: [sc2reader](https://github.com/ggtracker/sc2reader)
