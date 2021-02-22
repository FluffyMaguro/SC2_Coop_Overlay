var masteryNames = {
    'Abathur': ['Toxic Nest Damage', 'Mend Healing Duration', 'Symbiote Ability Improvement', 'Double Biomass Chance', 'Toxic Nest Maximum Charges and Cooldown', 'Structure Morph and Evolution Rate'],
    'Alarak': ['Alarak Attack Damage', 'Combat Unit Attack Speed', 'Empower Me Duration', 'Death Fleet Cooldown', 'Structure Overcharge Shield and Attack Speed', 'Chrono Boost Efficiency'],
    'Artanis': ['Shield Overcharge Duration and Damage Absorption', 'Guardian Shell Life and Shield Restoration', 'Energy Regeneration and Cooldown Reduction', 'Speed Increases for Warped In Units', 'Chrono Boost Efficiency', 'Initial and Maximum Spear of Adun Energy'],
    'Dehaka': ['Devour Healing Increase', 'Devour Buff Duration', 'Greater Primal Wurm Cooldown', 'Pack Leaders Active Duration', 'Gene Mutation Chance', 'Dehaka Attack Speed'],
    'Fenix': ['Fenix Suit Attack Speed', 'Fenix Suit Offline Energy Regeneration', 'Champion A.I. Attack Speed', 'Champion A.I. Life and Shields', 'Chrono Boost Efficiency', 'Extra Starting Supply'],
    'Horner': ['Strike Fighter Area of Effect', 'Stronger Death Chance', 'Significant Other Bonuses', 'Double Salvage Chance', 'Air Fleet Travel Distance', 'Mag Mine Charges, Cooldown, and Arming Time'],
    'Karax': ['Combat Unit Life and Shield', 'Structure Life and Shields', 'Repair Beam Healing Rate', 'Chrono Wave Energy Generation', 'Chrono Boost Efficiency', 'Initial and Maximum Spear of Adun Energy'],
    'Kerrigan': ['Kerrigan Energy Regeneration', 'Kerrigan Attack Damage', 'Combat Unit Vespene Gas Cost', 'Augmented Immobilization Wave', 'Expeditious Evolutions', 'Primary Ability Damage and Attack Speed'],
    'Nova': ['Nuke and Holo Decoy Cooldown', 'Griffin Airstrike Cost', 'Nova Primary Ability Improvement', 'Combat Unit Attack Speed', 'Nova Energy Regeneration', 'Unit Life Regeneration'],
    'Raynor': ['Research Resource Cost', 'Speed Increases for Drop Pod Units', 'Hyperion Cooldown', 'Banshee Airstrike Cooldown', 'Medics Heal Additional Target', 'Mech Attack Speed'],
    'Stetmann': ['Upgrade Resource Cost', 'Gary Ability Cooldown', 'Stetzone Bonuses', 'Maximum Egonergy Pool', 'Deploy Stetellite Cooldown', 'Structure Morph Rate'],
    'Stukov': ['Volatile Infested Spawn Chance', 'Infest Structure Cooldown', 'Aleksander Cooldown', 'Apocalisk Cooldown', 'Infested Infantry Duration', 'Mech Attack Speed'],
    'Swann': ['Concentrated Beam Width and Damage', 'Combat Drop Duration and Life', 'Immortality Protocol Cost and Build Time', 'Structure Health', 'Vespene Drone Cost', 'Laser Drill Build Time, Upgrade Time, and Upgrade Cost'],
    'Tychus': ['Tychus Attack Speed', 'Tychus Shredder Grenade Cooldown', 'Tri-Outlaw Research Improvement', 'Outlaw Availability', 'Medivac Pickup Cooldown', 'Odin Cooldown'],
    'Vorazun': ['Dark Pylon Range', 'Black Hole Duration', 'Shadow Guard Duration', 'Time Stop Unit Speed Increase', 'Chrono Boost Efficiency', 'Initial and Maximum Spear of Adun Energy'],
    'Zagara': ['Zagara And Queen Regen', 'Zagara Attack Damage', 'Intensified Frenzy', 'Zergling Evasion', 'Roach Damage and Life', 'Baneling Attack Damage'],
    'Zeratul': ['Zeratul Attack Speed', 'Combat Unit Attack Speed', 'Artifact Fragment Spawn Rate', 'Support Calldown Cooldown Reduction', 'Legendary Legion Cost', 'Avatar Cooldown'],
    'Mengsk': ['Laborer and Trooper Imperial Support', 'Royal Guard Support', 'Terrible Damage', 'Royal Guard Cost  ', 'Starting Imperial Mandate', 'Royal Guard Experience Gain Rate']
};

// Start
var showmutators = true;
var function_is_running = false;
var PORT = 7305;
var DURATION = 60;
var maxUnits = 5;
var gP1Color = '#0080F8';
var gP2Color = '#00D532';
var toBeShown = false;
var winrateTime = 12;
var showingWinrateStats = false;
var last_shown_file = '';
var do_not_use_websocket = false;
var minimum_kills = 1; // minimum number of kills for a unit to be shown

//main functionality
setColors(null, null, null, null);
setTimeout(function(){
        connect_to_socket();                  
        document.getElementById('bgdiv').style.display = 'block';
        document.getElementById('ibgdiv').style.display = 'block';              
       }, 500);

function connect_to_socket() {
    if (function_is_running) {
        return
    };
    if (do_not_use_websocket) {
        return
     };
    function_is_running = true;
    let socket = new WebSocket("ws://localhost:" + PORT);
    socket.onopen = function(e) {};
    socket.onmessage = function(event) {
        if (do_not_use_websocket) {
                socket.onclose = function() {};
                socket.close();
                return
             };
        var data = JSON.parse(event.data);
        console.log('New event');
        if (data['replaydata'] != null) {
            postGameStatsTimed(data)
        } else if (data['mutatordata'] != null) {
            mutatorInfo(data['data'])
        } else if (data['hideEvent'] != null) {
            hidestats()
        } else if (data['showEvent'] != null) {
            showstats()
        } else if (data['showHideEvent'] != null) {
            showhide()            
        } else if (data['uploadEvent'] != null) {
            setTimeout(uploadStatus, 1500, data['response'])
        } else if (data['initEvent'] != null) {
            initColorsDuration(data)
        } else if (data['playerEvent'] != null) {
            showHidePlayerWinrate(data)
        } else {
            console.log('unidentified message')
        }
    };
    socket.onclose = function(event) {
        if (event.wasClean) {
            console.log('CLEAN EXIT: ' + event)
        } else {
            console.log('UNCLEAN EXIT: ' + event)
        };
        reconnect_to_socket();
    };
    socket.onerror = function(error) {
        console.log('ERROR: ' + error);
        reconnect_to_socket()
    };
}

function reconnect_to_socket(message) {
    console.log('Reconnecting..')
    function_is_running = false;
    setTimeout(function() {
        connect_to_socket();
    }, 1000);
}


function showHidePlayerWinrate(dat) {
    if (showingWinrateStats) {
        showingWinrateStats = false;
        document.getElementById('playerstats').style.right = '-60vh';
        document.getElementById('playerstats').style.opacity = '0';
      } else {
        playerWinrate(dat)
      }
}


function playerWinrate(dat) {
    var element = document.getElementById('playerstats');
    var text = '';
    showingWinrateStats = true;

    for (let [key, value] of Object.entries(dat['data'])) {
        // no data ([None])
        if ((value.length == 1) && (value[0] == null)) {
            text += 'No games played with <span class="player_stat">' + key + '</span>'

        // no winrate data but with a player note ([None, note])
        } else if ((value.length == 2) && (value[0] == null)) {
            text += 'No games played with <span class="player_stat">' + key + '</span><br>' + value[1]

        // winrate data ([wins, losses, apm, commander, frequency])
        } else if (value.length == 6) {
            let total_games = value[0] + value[1];
            text += 'You played ' + total_games + ' games with <span class="player_stat">' + key + '</span> (' + Math.round(100 * value[0] / total_games) + '% winrate) (' + Math.round(100 * value[5]) + '% kills)'

        // winrate data and player note ([wins, losses, apm, commander, frequency, note])
        } else if (value.length == 7) {
            let total_games = value[0] + value[1];
            text += 'You played ' + total_games + ' games with <span class="player_stat">' + key + '</span> (' + Math.round(100 * value[0] / total_games) + '% winrate) ('+ Math.round(100 * value[5]) + '% kills)<br>' + value[6]
        }
    }
    element.innerHTML = text;
    element.style.right = '2vh';
    element.style.opacity = '1';
    setTimeout(function() {
        document.getElementById('playerstats').style.right = '-60vh';
        document.getElementById('playerstats').style.opacity = '0';
        showingWinrateStats = false;
    }, winrateTime*1000)
}


function initColorsDuration(data) {
    setColors(data['colors'][0], data['colors'][1], data['colors'][2], data['colors'][3]);
    DURATION = data['duration'];
}


function setColors(P1color, P2color, P3color, MasteryColor) {
    //this function is executed by the app on page load
    //Player 1
    if (P1color != null) {
        gP1Color = P1color
    };
    document.getElementById('name1').style.color = gP1Color;
    document.getElementById('CMname1').style.color = gP1Color;
    document.getElementById('killbar1').style.backgroundColor = gP1Color;
    document.getElementById('CMtalent1').style.color = gP1Color;

    //Player 2
    if (P2color != null) {
        gP2Color = P2color
    };

    document.getElementById('name2').style.color = gP2Color;
    document.getElementById('CMname2').style.color = gP2Color;
    document.getElementById('killbar2').style.backgroundColor = gP2Color;
    document.getElementById('CMtalent2').style.color = gP2Color;

    //Player 3
    var color = '#FF0000';
    if (P3color != null) {
        color = P3color
    };
    document.getElementById('CMname3').style.color = color;
    document.getElementById('comp').style.color = color;

    //Mastery
    color = '#FFDC87';
    if (MasteryColor != null) {
        color = MasteryColor
    };
    document.getElementById('CMmastery1').style.color = color;
    document.getElementById('CMmastery2').style.color = color;
}

function uploadStatus(result) {
    var loader = document.getElementById('loader');
    var tshowing = DURATION * 1000;

    loader.style.transition = 'opacity 0s';
    loader.style.opacity = '0'
    loader.style.transition = 'opacity 1s';
    loader.innerHTML = ''
    loader.style.opacity = '1';

    if (result.includes('Success')) {
        loader.style.color = 'rgba(0, 150, 0, 1)';
        loader.innerHTML = 'Replay uploaded successfully!';
    } else {
        loader.style.color = 'rgba(225, 0, 0, 1)';
        loader.innerHTML = 'Replay not uploaded!<br>' + result;
    };
}

function mutatorInfo(data) {
    if (!(showmutators)) {
        return
    };
    var mduration = 15 * 1000;
    if (data.length > 6) {
        document.getElementById('mutatorinfo').style.width = '133vh';
    }
    for (i = 0; i < data.length; i++) {
        var divelement = document.getElementById('mut' + i);
        divelement.getElementsByTagName("img")[0].src = '../HQ Mutator Icons/' + data[i][0] + '.png';
        divelement.getElementsByTagName("p")[0].innerHTML = '<span class="muttop">' + data[i][0] + '</span><span class="mutvalue"> ' + data[i][1] + '</span><br><span class="mutdesc">' + mutatorDescriptions[data[i][0]] + '</span>';
        divelement.style.display = 'inline-block';
        setTimeout(function(el) {
            el.style.opacity = '1'
        }, i * 400, divelement);
        setTimeout(function(el) {
            el.style.opacity = '0'
        }, mduration, divelement);
        setTimeout(function(el) {
            el.style.display = 'none'
        }, mduration + 5000, divelement);
    }
}

function postGameStatsTimed(data) {
    //This is a wrapper for postGameStats
    //The goal is to nicely update the data if it's already showing
    if ((document.getElementById('stats').style.right != '-50vh') && (document.getElementById('stats').style.right != '')) {

        // If we are about to show the same data, hide instead
        if (last_shown_file == data['file']) {
            hidestats()
        } else {
            document.getElementById('stats').style.opacity = '0';
            setTimeout(function() {
                document.getElementById('stats').style.opacity = '1'
            }, 300);
            setTimeout(postGameStats, 300, data, showing = true);
        }

    } else {
        postGameStats(data);
    }
}

function format_length(seconds) {
    var gseconds = Math.round(seconds * 1.4);
    var sec = gseconds % 60;
    var min = ((gseconds - sec) / 60) % 60;
    var hr = (gseconds - sec - min * 60) / 3600;

    if (hr > 0) {
        hr = hr + ':'
    } else {
        hr = ''
    }

    if (min == 0) {
        min = '00:'
    } else if (min < 10) {
        min = '0' + min + ':'
    } else {
        min = min + ':'
    }

    if (sec < 10) {
        sec = '0' + sec
    }
    return hr + min + sec
}

function fillCommander(el, commander, commander_level) {
    var addition = '';
    if (commander == null) {
        return
        }
    if (commander_level < 15) {
        addition = '{'+commander_level+'}'
        }
    if (el == 'com1') {
        fill(el,commander+' '+addition)
       } else {
        fill(el,addition+' '+commander)
       }
}

function postGameStats(data, showing = false) {
    //initial change
    document.getElementById('killbar').style.display = 'block';
    document.getElementById('nodata').style.display = 'none';
    //fill
    fill('CMtalent1',data['mainPrestige'])
    fill('CMtalent2',data['allyPrestige'])
    fill('comp', data['comp']);

    // save file name
    last_shown_file = data['file'];

    //Bonus objectives
    var bonus_text = '';
    for (i = 0; i < data['bonus'].length; i++) {
        if (i == 0) {
            bonus_text = data['bonus'][i]
        } else {
            bonus_text = bonus_text + ' | ' + data['bonus'][i]
        }                                            
    }
    fill('bonus', bonus_text);

    // Mutators
    var mutator_text = '';
    if ((data['mutators'] != null) && (data['mutators'].length > 0)) {
        for (i = 0; i < data['mutators'].length; i++) {
            mutator_text = mutator_text + '<img src="Mutator Icons/' + data['mutators'][i] + '.png">'
        }
        fill('mutators', mutator_text);
        fill('result', data['result'] + '!');
    } else {
        fill('mutators', '<span id="resultsp">' + data['result'] + '!</span>');
        fill('result', 'kills');
    }
    

    //BG images
    if ((data['mainCommander'] != null) && (data['mainCommander'] != '')) {
        document.getElementById('killbar1img').src ='Commanders/'+ data['mainCommander'] +'.png'
    } else {
        document.getElementById('killbar1img').src =''
    }
    if ((data['allyCommander'] != null) && (data['allyCommander'] != '')) {
        document.getElementById('killbar2img').src ='Commanders/'+ data['allyCommander'] +'.png'
    } else {
        document.getElementById('killbar2img').src =''
    }    

    fill('name1', data['main']);
    
    fill('map', data['map_name'] + '&nbsp;&nbsp;(' + format_length(data['length']) + ')');
    fill('name2', data['ally']);
    fillCommander('com1', data['mainCommander'], data['mainCommanderLevel'])
    fillCommander('com2', data['allyCommander'], data['allyCommanderLevel'])
    fill('apm1', data['mainAPM'] + ' APM');
    fill('apm2', data['allyAPM'] + ' APM');

    if (data['fastest'] == true) {
        document.getElementById('record').style.display = 'block';
    } else {
        document.getElementById('record').style.display = 'none';
    }

    if (data['Victory'] != null) {
        fill('session', 'Session: ' + data['Victory'] + ' wins/' + (data['Victory'] + data['Defeat']) + ' games');
    } else {
        fill('session', '');
    };

    if (data['Commander'] != null) {
        fill('rng', 'Randomized commander: ' + data['Commander'] + ' (' +  data['Prestige'] + ')');
    } else {
        fill('rng', '');
    };    

    if ((data['extension'] > 0) && (data['mutators'] != null) && (data['mutators'].length == 0)) {
        fill('brutal', 'Weekly ('+ data['difficulty'] + ')' ) 
    } else if ((data['extension'] > 0) && (data['mutators'] != null)) { 
        fill('brutal', 'Custom ('+ data['difficulty'] + ')' )
    } else if (data['B+'] > 0) {
        fill('brutal', 'Brutal+' + data['B+'])
    } else {
        fill('brutal', data['difficulty'])
    };

    // kill counts
    var killbarW = document.getElementById('killbar').offsetWidth;
    var totalkills = data['mainkills'] + data['allykills']
    if (totalkills > 0) {
        var percent1 = Math.round(100 * data['mainkills'] / totalkills) + '%';
        var percent2 = Math.round(100 * data['allykills'] / totalkills) + '%';
        document.getElementById('killbar1').style.backgroundColor = gP1Color;
        document.getElementById('killbar2').style.backgroundColor = gP2Color;
        //delay unless it's already being showed
        if (!(showing)) {
            setTimeout(function() {
                document.getElementById('killbar1').style.width = percent1;
                document.getElementById('killbar2').style.width = percent2;
            }, 700)
        } else {
            document.getElementById('killbar1').style.width = percent1;
            document.getElementById('killbar2').style.width = percent2
        };
        fill('percent1', percent1);
        fill('percent2', percent2);
    } else {
        document.getElementById('killbar1').style.width = '50%';
        document.getElementById('killbar2').style.width = '50%';
        document.getElementById('killbar1').style.backgroundColor = '#666';
        document.getElementById('killbar2').style.backgroundColor = '#444';
        fill('percent1', '0%');
        fill('percent2', '0%');
    };

    //player stats
    fill('CMname1', data['main']);
    fillicons('CMicons1', data['mainIcons']);
    fillmasteries('CMmastery1', data['mainMasteries'], data['mainCommander']);
    fillunits('CMunits1', data['mainUnits'], data['mainCommander']);

    fill('CMname2', data['ally']);
    fillicons('CMicons2', data['allyIcons']);
    fillmasteries('CMmastery2', data['allyMasteries'], data['allyCommander']);
    fillunits('CMunits2', data['allyUnits'], data['allyCommander']);

    fill('CMname3', 'Amon');
    fillunits('CMunits3', data['amon_units'], null);
    //show
    showstats();

    //victory data is for automatic showing. In that case automatically hide. Otherwise hide loader.
    if (data['Victory'] == null) {
        document.getElementById('loader').style.opacity = '0';
        document.getElementById('loader').innerHTML = ''
    } 
    if (data['newReplay'] != null) {
        setTimeout(hidestats, DURATION * 1000);
    }
}

function showhide() {
    if (!toBeShown) {
        showstats()
    } else {
        hidestats()
    }
}

function hidestats() {
    toBeShown = false;
    document.getElementById('stats').style.right = '-50vh';
    document.getElementById('bgdiv').style.opacity = '0';
    document.getElementById('loader').style.opacity = '0';
    document.getElementById('session').style.opacity = '0';
    document.getElementById('rng').style.opacity = '0';
    setTimeout(function() {
        document.getElementById('session').innerHTML = '';
        document.getElementById('rng').innerHTML = '';
        document.getElementById('loader').style.opacity = '0';
        document.getElementById('loader').innerHTML = ''
    }, 1000)
}

function showstats() {
    toBeShown = true;
    document.getElementById('stats').style.right = '2vh';
    document.getElementById('bgdiv').style.opacity = '1';
    setTimeout(function(){document.getElementById('session').style.opacity = '0.6'; document.getElementById('rng').style.opacity = '1'},1000)

}

function fill(el, dat) {
    document.getElementById(el).innerHTML = dat;
}

function fillmasteries(el, dat, commander) {
    var text = '';
    if ((dat == null) || (commander == null) || (commander == '') || (masteryNames[commander] == null)) {
        document.getElementById(el).innerHTML = '';
        return
    };
    var any_mastery = false;
    for (i = 0; i < dat.length; i++) {
        var spacer = '<span>';

        if (dat[i] < 10) {
            spacer = '<span class="">&nbsp;&nbsp;'
        }

        if (dat[i] == 0) {
            spacer = '<span class="nomastery">&nbsp;&nbsp;'
        } else {
            any_mastery = true;
        }

        text = text + spacer + dat[i] + ' ' + masteryNames[commander][i] + '<br></span>';

    }

    if (any_mastery) {
        document.getElementById(el).style.display = 'block';
    } else {
        document.getElementById(el).style.display = 'none';
    }


    document.getElementById(el).innerHTML = text;
}

function fillicons(el, data) {
    var text = '';
    for (let [key, value] of Object.entries(data)) {
        if (key == 'outlaws') {
            for (i = 0; i < data['outlaws'].length; i++) {
                text = text + '<img src="Icons/' + data['outlaws'][i] + '.png">';
            }

        } else if ((['hfts', 'tus', 'propagators', 'voidrifts', 'turkey', 'voidreanimators', 'deadofnight', 'minesweeper'].includes(key)) && (value > 0)) {
            text = text + '<img src="Icons/' + key + '.png"> <span class="icontext">' + value + '</span>';

        } else if ((key == 'killbots') && (value > 0)) {
            text = text + '<img src="Icons/' + key + '.png"> <span class="icontext killbotkills">-' + value + '</span>';

        } else if (value > 0) {
            text = text + '<img src="Icons/' + key + '.png"> <span class="icontext iconcreated">+' + value + '</span>';
        }
    }
    document.getElementById(el).innerHTML = text
}

function fillunits(el, dat, commander) {
    let text = '<span class="unitkills">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;kills</span><span class="unitcreated">created</span><span class="unitdied">lost</span><br>';
    let percent = 0;
    let spacer = '';
    let idx = 0;
    if (dat == null) {
        return
    };
    for (let [key, value] of Object.entries(dat)) {
        if (idx === maxUnits) {
            break
        };

        // Switch few unit names
        if ((key == 'Stalker') && (commander == 'Alarak')) {key = 'Slayer'};
        if ((key == 'Sentinel') && (commander == 'Fenix')) {key = 'Legionnaire'};

        spacer = '';
        percent = Math.round(100 * value[3]);
        if (percent < 10) {
            spacer = 'killpadding'
        } else if (percent == 100) {
            spacer = 'nokillpadding'
        };
        if (value[2] >= minimum_kills) {
            idx += 1;                   
            text = text + key + ' <span class="unitkills ' + spacer + '">' + percent + '% | ' + value[2] + '</span>  <span class="unitcreated">' + value[0] + '</span>  <span class="unitdied">' + value[1] + '</span><br>'
        };
    }

    if (idx == 0) {
        text = '<span class="unitkills"></span>'
    }
    document.getElementById(el).innerHTML = text;
}