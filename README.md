# StarCraft II Coop Overlay (SCO)
* [**DOWNLOAD HERE**](https://github.com/FluffyMaguro/SC2_Coop_overlay/releases/download/2.45/SC2CoopOverlay.2.45.zip)

* Or run the script with Python 3.6+:

```
pip install -r requirements.txt
python SCO.py
```

The app shows an overlay with replay analysis of StarCraft II Co-op games. It also provides match history, various statistics based on your replays, commander randomizer, info about players shown at the start of the game, custom twitch bot with game integration into MM maps, and more.

For streamers the the overlay can be added as another layer in Open Broadcaster Software (OBS) or other streaming software applications. It's fully customizable through simple editing of the HTML, CSS and JS files. 

For bugs, feedback and suggestions check [my discord](https://discord.com/invite/FtGdhqD).



Info shown after a game:
![Screenshot](https://i.imgur.com/4fipWEZ.jpg)

![Screenshot](https://i.imgur.com/PTZ8Nwn.png)

Info shown at the start of a game:
<img width="100%" alt="Overlay info at the start" src="https://i.imgur.com/1hrMteQ.png">

# How to use
1. Extract the archive
2. Run the executable (SCO.exe)
4. Some anti-virus programs are very sensitive to packaged python apps. If you have issues, add an exception to your anti-virus for the directory the app is in.
5. Use hotkeys or buttons in the app to control the overlay. It will show automatically after each game as well.
5. In StarCraft II set display mode to Windowed fullscreen (borderless)

To exit the app right click the icon in the system tray and click "Quit".

![Screenshot](https://i.imgur.com/zq8DBy8.jpg)


# OBS setup

If you are using game capture, you have to add overlay to OBS manually.

<img width="100%" alt="Drag the layout file to OBS" src="https://i.imgur.com/ECARj6M.png">

<img width="52.38%" alt="Fit the layout to screen" src="https://i.imgur.com/dNSWhq4.png">

# Screenshots
**Settings:**

![Screenshot](https://i.imgur.com/FU6vL5y.png)

**Settings (Dark theme):**

![Screenshot](https://i.imgur.com/m2RKl5U.png)

**List of games you recently played:**

![Screenshot](https://i.imgur.com/THvYdpf.png)

**List of players you played with:**

![Screenshot](https://i.imgur.com/ndrOQ4A.png)

**Map statistics:**

![Screenshot](https://i.imgur.com/eY2quJ6.png)

**Statistics for your and allied commanders:**

![Screenshot](https://i.imgur.com/YTts8u6.png)

**Unit statistics:**

![Screenshot](https://i.imgur.com/knFR51v.png)

**Commander randomizer:**

![Screenshot](https://i.imgur.com/4P4ga0L.png)


**Twitch chat overlay:**

![Screenshot](https://i.imgur.com/JLH9AJA.jpg)

**Performance overlay:**

![Screenshot](https://i.imgur.com/Z9Ekvdx.jpg)
**And more...**


# Other notes
* The overlay targets Windows 10. It might not work correctly on older versions of windows (black background under overlay).
On Windows 7 enable aero theme and set “Enable Transparency” in “Window Color”.
* On MacOS or Linux run the script with "`sudo python3 SCO.py`" after installing required packages. It has been successfully tested on both MacOS and Linux, however every distribution and OS version has its own quirks.
* The app connects to the internet only at start to look for a new version, or if you setup automatic replay upload by filling in accout name and password.
* The app is not in conflict with Blizzard's Terms of Service. It uses official Blizzard's library (s2protocol) to parse replays, and what information StarCraft II provides while running.
* You can edit the layout .html file. Changing its style through CSS (custom.css) or other functionality with javascript (custom.js).
* Indirectly killed Interceptors are counted towards player kills which is not the case in kills showed in-game. Directly killed interceptors are counted in both cases.


# Overlay customization

For customization locate **custom.css** and **custom.js** in the overlay folder (in Layouts/).
These files contain your customization and are not overridden when the the overlay updates.

**1. Change the number of units shown**

Add this to *custom.js* and change the value. Higher numbers might overlap with other elements or won't fit onscreen.
```javascript
maxUnits = 5;
```
**2. Hide bars under units**

Add this to *custom.css*
```css
.unitkillbg {
    opacity: 0;
}
```
**3. Hide certain charts**

Add this to *custom.js*, and remove those that you don't want.
```javascript
CC = {
    'army': null,
    'supply': null,
    'killed': null,
    'mining': null
  }
  ```

**4. Custom function that runs when new replay data is filled**

Add something like this to custom.js. The function will run when new data is added.

```javascript
func_on_new_data = function some_function_name(data) {
    // This shows you what's the structure of replay data (can be removed)
    for(var key in data) {
        console.log(key + ":\t\t" + data[key] + "\t\t")
    }
}
```


# Changelog

[Releases and changelog](https://github.com/FluffyMaguro/SC2_Coop_Overlay/releases)

# Config file

**Twitch bot** can be set up in this way.
*bot_oauth* has to be generated by twitch for example [here](https://twitchapps.com/tmi/). It's also possible to change in the config file greetings, banned units and mutators, and reponses to user commands.


```
  "twitchbot": {
    "channel_name": "fluffymaguro",
    "bot_name": "veryfluffybot",
    "bot_oauth": "oauth:r8b5...............",
    "bank_locations": {
      "Default": "C:/Users/Maguro/Documents/StarCraft II/Accounts/114803619/1-S2-1-4189373/Banks/1-S2-1-4189373/MMTwitchIntegration.SC2Bank",
      "Local": "C:/Users/Maguro/Documents/StarCraft II/Banks/MMTwitchIntegration.SC2Bank",
      "EU": "C:/Users/Maguro/Documents/StarCraft II/Accounts/452875987/2-S2-1-7503439/Banks/2-S2-1-1174830/MMTwitchIntegration.SC2Bank"
      },

      ...

   }
```

You can change the **offset from the right side of the monitor**.
Negative values mean more to the left.

```
"right_offset": 0,
```

You can change the **font size** by a relative scaling factor. Default is 1.

```
"font_scale": 1,
```