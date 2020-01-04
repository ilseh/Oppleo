/* TODO
- flot database
  - last 10 occurrences
  - max/ min
- kleurenlamp buiten
- kleurenlamp bed ledstrip fibaro
- lux device
- alarm (smoke, ...)
- refresh knop op honeywel evohome
- fix counter op evohome
- RING video
- bose device (https://developer.bose.com/soundtouch-control-api/apis)
  - speel over alle apparaten
- power toevoegen aan blokken (incl. uppdate), misschien geen getal maar wel een geel bliksem symbool?
- power
- energie
- camerabeeld (garage, ring)
- audi myaudi location view
  https://github.com/davidgiga1993/AudiAPI/tree/master/audiapi
- prevent mixed content - load SoundTouch images through splash

done:
- audi
- life360 location view
  https://github.com/SmartThingsCommunity/SmartThingsPublic/blob/a62d825f6947408e38023ed21f64097d360b139c/smartapps/smartthings/life360-connect.src/life360-connect.groovy
- bose device (https://developer.bose.com/soundtouch-control-api/apis)
  - voorkeursknoppen
  - wat speelt nu
- Neato API
- login - automatiseren + naam
  - foto!
  - nalogin terug naar gewenste pagina
  - bij webapp store location local en ga daarnaartoe na login
- ventilator badkamer
  - slider met uit-low-med-high low:links aan rechts uit, med: links uit rechts aan hight: beide aan
- Harmony
	https://www.myharmony.com/en-us/harmony-api
	https://docs.google.com/document/d/1fjPMr0eLJWaFoZw0JMu449dgKFXR0K1m6EoxsDbgt8I/pub
- weer blok
- humidity device
- temp device
- honeywell device
- woonkamer licht device
- light (switch & dimmer)
- batterij
- uptime device

*/

// All the Temperature devices
var devicelist_temp = [	[ 342, 'Deursensor', 'Aeotec'],
 						[ 346, 'Motion sensor', 'Fibaro Eye' ], 
    					[ 357, 'Motion sensor', 'Fibaro Eye' ], 
    					[ 364, 'Deursensor', 'Aeotec' ], 
    					[ 463, 'Smoke sensor', 'Fibaro FGSD-002' ], 
    					[ 609, 'Motion sensor', 'Fibaro Eye' ], 
    					[ 674, 'Motion sensor', 'Fibaro Eye' ], 
    					[ 711, 'Thermo/Hygro sensor', 'Everspring Multilevel Sensor' ], 
    					[ 742, 'Thermo/Hygro sensor', 'Oregon THGN800' ]
    				];

// All the Light devices - for now in Woonkamer
var devicelist_light = [[ 298, true, 'Dimmer', 'Van wie?'],
 						[ 422, true, 'Dimmer', 'Van wie?' ], 
    					[ 738, false, 'Switch', 'Van wie?' ]
    				];

// All the Evohome zones
var evohomeZones = [	[ 2069237, 'Badkamer 1' ],
 						[ 2306137, 'Badkamer 2' ], 
    					[ 2329524, 'Balzaal' ], 
    					[ 2069263, 'Gang' ], 
    					[ 2329554, 'Logeerkamer' ], 
    					[ 2329571, 'Slaapkamer' ], 
    					[ 2330410, 'Vloer' ], 
    					[ 2297923, 'Washok' ], 
    					[ 2069120, 'Woonkamer' ]
    				];

// All the devices
//  ref
//  location
//  js object
//  power
var hsDevices = [[ 267, 'Meterkast',	'SplashEnergyDevice',	null ], // Meterkast Current total usage
 				 [ 269, 'Meterkast',	'SplashEnergyDevice',	null ], // Elektra huidig verbruik vandaag max
 				 [ 268, 'Meterkast',	'SplashEnergyDevice',	null ], // Elektra huidig verbruik vandaag min
                 [ 270, 'Meterkast',    'SplashEnergyDevice',   null ], // Gas verbruik
                 [ 271, 'Meterkast',    'SplashEnergyDevice',   null ], // Gas verbruik totaal
                 [ 272, 'Meterkast',    'SplashEnergyDevice',   null ], // Elektra huidige teruglevering
                 [ 273, 'Meterkast',    'SplashEnergyDevice',   null ], // Elektra teruglevering vandaag min
                 [ 274, 'Meterkast',    'SplashEnergyDevice',   null ], // Elektra teruglevering vandaag max
				 [ 298, 'Woonkamer',	'SplashLightDevice',	null ], // Woonkamer Buislamp
 				 [ 342, 'Gardarobe',	'',						null ], // Gardarobe Doorsensor Battery
 				 [ 344, 'Gardarobe',	'',						null ], // Gardarobe Doorsensor Open/Closed
 				 [ 346, 'Gardarobe',	'',						null ], // Gardarobe Eye Batterij (loadTemperatureDevice)
 				 [ 348, 'Gardarobe',	'SplashMotionDevice',	null ], // Gardarobe Eye Motion
 				 [ 349, 'Gardarobe',	'SplashTempDevice',		null ], // Gardarobe Eye Temperature
 				 [ 350, 'Gardarobe',	'SplashLuminanceDevice',        null ], // Gardarobe Eye Luminance (LUX)
 				 [ 377, 'Woonkamer',	'SplashLightDevice',	null ], 
 				 [ 359, 'Garage',		'SplashMotionDevice',	null ], // Garage Bewegingssensor
 				 [ 360, 'Garage',		'SplashTempDevice',		null ], // Garage Temperatuur
 				 [ 361, 'Garage',		'SplashLuminanceDevice',        null ], // Garage Lux
 				 [ 422, 'Woonkamer',	'SplashLightDevice',	null ], // Woonkamer tripodlamp
  				 [ 436, 'Gardarobe',	'SplashLightDevice',	null ], // Plafondlamp gardarobe
 				 [ 439, 'Garage',		'SplashLightDevice',	null ], // Garage Plafondlamp 
 				 [ 440, 'Garage',		'SplashOneButtonFanDevice',	    null ], // Ventilator
 				 [ 441, 'Keuken',		'SplashLightDevice',	null ], // Keuken plafondspots
                 [ 442, '2e Overloop',  'SplashLightDevice',    null ], // 2e overloop plafondspots
                 [ 445, 'Washok',       'SplashEnergyDevice',   null ], // Washok Wasmachine kWh
                 [ 448, 'Washok',       'SplashEnergyDevice',   null ], // Washok Wasmachine Power
                 [ 451, 'Washok',       'SplashEnergyDevice',   null ], // Washok Droogtrommel kWh
                 [ 453, 'Washok',       'SplashEnergyDevice',   null ], // Washok Droogtrommel Power
                 [ 505, 'Gang',         'SplashEnergyDevice',   null ], // Designlamp kWh
                 [ 506, 'Gang',         'SplashEnergyDevice',   null ], // Designlamp Watt
                 [ 507, 'Gang',         'SplashEnergyDevice',   null ], // Designlamp Power
                 [ 508, 'Gang',         'SplashLightDevice',    null ], // Designlamp
                 [ 515, '1e Overloop',  'SplashEnergyDevice',   null ], // 1e overloop plafondspots kWh
                 [ 516, '1e Overloop',  'SplashEnergyDevice',   null ], // 1e overloop plafondspots Watt
                 [ 518, '1e Overloop',  'SplashLightDevice',    null ], // 1e overloop plafondspots
    		  	 [ 541, 'Voortuin', 	'SplashUptimeDevice',	null ],	// Ring Doorbell Pro
    		  	 [ 542, 'Meterkast', 	'SplashUptimeDevice',	null ],	// Ring Chime
    		  	 [ 544, 'Overloop 1e', 	'SplashUptimeDevice',	null ],	// Ring Chime
    		  	 [ 545, 'Overloop 2e', 	'SplashUptimeDevice',	null ],	// Ring Chime
                 [ 595, 'Slaapkamer',   'SplashEnergyDevice',   null ], // Wandlampen kW Hours
                 [ 596, 'Slaapkamer',   'SplashEnergyDevice',   null ], // Wandlampen Watt
                 [ 597, 'Slaapkamer',   'SplashEnergyDevice',   null ], // Wandlampen Power
    		  	 [ 598, 'Slaapkamer', 	'SplashLightDevice',	null ],	// Wandlampen
                 [ 634, 'Meterkast',    'SplashEnergyDevice',   null ], // Verbruik netwerk totaal
                 [ 635, 'Meterkast',    'SplashEnergyDevice',   null ], // Verbruik netwerk vandaag
                 [ 661, 'Inloopkast',   'SplashLightDevice',    null ], // Wandspots inloopkast
                 [ 669, 'Inloopkast',   'SplashEnergyDevice',   null ], // Wandspots kWh
                 [ 670, 'Inloopkast',   'SplashEnergyDevice',   null ], // Wandspots Watt
    		  	 [ 684, 'CV-ruimte', 	'SplashUptimeDevice',	null ],	// ASUS RT-AC66U
    		  	 [ 686, 'Badkamer 2', 	'SplashLightDevice',	null ],	// Badkamer led spots
                 [ 694, 'Badkamer 2',   'SplashEnergyDevice',   null ],  // Badkamer Lampen kWh 
                 [ 695, 'Badkamer 2',   'SplashEnergyDevice',   null ],  // Badkamer Lampen Watt 
                 [ 697, 'Badkamer 2',   'SplashTwoButtonFanDevice',     699 ],  // Badkamer Fan Links 
    		  	 [ 699, 'Badkamer 2', 	'SplashTwoButtonFanDevice',		697 ],	// Badkamer Fan Rechts
                 [ 705, 'Badkamer 2',   'SplashEnergyDevice',   null ], // Badkamer 2 FAN kWh
                 [ 706, 'Badkamer 2',   'SplashEnergyDevice',   null ], // Badkamer 2 FAN Watt
                 [ 708, 'Badkamer 2',   'SplashTempDevice',     null ], // Temperatuur
    		  	 [ 709, 'Badkamer 2',	'SplashHumidDevice',	null ], // Luchtvochtigheid
    		  	 [ 730, 'Overloop 1e', 	'SplashUptimeDevice',	null ],	// Ubiquiti Unify UAP-AC-Pro
    		  	 [ 732, 'Woonkamer', 	'SplashUptimeDevice',	null ],	// Raspberry Pi
                 [ 735, 'Woonkamer',    'SplashEnergyDevice',   null ], // Washok Droogtrommel kWh
                 [ 736, 'Woonkamer',    'SplashEnergyDevice',   null ], // Washok Droogtrommel Watts
                 [ 737, 'Woonkamer',    'SplashEnergyDevice',   null ], // Washok Droogtrommel Power
    		  	 [ 738, 'Woonkamer',	'SplashLightDevice',	null ],	// Woonkamer Vlechtlamp
    		  	 [ 740, 'Tuin',			'SplashTempDevice',		null ], // Tuintemperatuur
    		  	 [ 741, 'Tuin',			'SplashHumidDevice',	null ], // Tuin luchtvochtigheid
    		  	 [ 756, 'Slaapkamer',	'SplashEvohomeDevice',	null ], // Evohome
    		  	 [ 797, 'Woonkamer',	'SplashHarmonyDevice',	null ], // Harmony - Activity (1: PowerOff, 2: TV kijken, 3: Radio, 4: Flubbertje muziek, 5: Flubbertje, 6: iTV met Marantz, 7: Gramofon)
    		  	 [ 798, 'Woonkamer',	'SplashHarmonyDevice',	null ], // Harmony - TV ontvanger (1: PowerToggle, 2: 0, 3: 1, 4: 2, 5: 3, 6: 4, 7: 5, 8: 6, 9: 7, 10: 8, 11: 9, 12: Mute, 13: Channel Down, 14: ChannelUp, 15: DirectionDown, 16: DirectionLeft, 17: DirectionRight, 18: DirectionUp, 19: Select, 20: Stop, 21: Rewind, 22: Pause, 23: FastForward, 24: Record, 25: SlowForward, 26: Menu, 27: Teletext, 28: Green, 29: Red, 30: Blue, 31: Yellow, 32: Guide, 33: Info, 34: Cancel, 36: Radio, 39: TV)
    		  	 [ 799, 'Woonkamer',	'SplashHarmonyDevice',	null ], // Harmony - Receiver (1: PowerOff, 2: PowerOn, 16: Mute, 17: VolumeDown, 18: VolumeUp)
    		  	 [ 800, 'Woonkamer',	'SplashHarmonyDevice',	null ], // Harmony - ChromeCast Flubbertje
    		  	 [ 801, 'Woonkamer',	'SplashHarmonyDevice',	null ], // Harmony - TV (1: PowerOff, 2: PowerOn, 14: Mute, 15: VolumeDown, 16: VolumeUp, 41: AmbiLight, 42: AmbiMode)
    		  	 [ 802, 'Meterkast', 	'SplashUptimeDevice',	null ],	// ASUS RT-AC68U
    		  	 [ 803, 'Meterkast', 	'SplashUptimeDevice',	null ],	// DiskStation
    		  	 [ 804, 'Badkamer 2', 	'SplashUptimeDevice',	null ],	// Bose SoundTouch 20
    		  	 [ 805, 'Woonkamer', 	'SplashUptimeDevice',	null ],	// Gramofon
    		  	 [ 806, 'CV Ruimte', 	'SplashUptimeDevice',	null ],	// Diskstation
    		  	 [ 807, 'Garage',	 	'SplashUptimeDevice',	null ],	// Camera
    		  	 [ 808, 'CV Ruimte', 	'SplashUptimeDevice',	null ],	// Ubiquiti Unify UAP-AC-Pro   		  	 
    		  	 [ 809, 'Meterkast', 	'SplashUptimeDevice',	null ],	// Netgear GS724T
    		  	 [ 811, 'Meterkast', 	'SplashUptimeDevice',	null ],	// NUC    		  	 
    		  	 [ 812, 'Woonkamer', 	'SplashUptimeDevice',	null ],	// Ubiquiti UnifyIn-Wall AC Pro    		  	 
    		  	 [ 814, 'Woonkamer', 	'SplashLightDevice',	null ],	// Eettafel plafondlamp    		  	 
                 [ 820, 'Woonkamer',    'SplashEnergyDevice',   null ], // Eettafel plafondlamp kWh             
                 [ 821, 'Woonkamer',    'SplashEnergyDevice',   null ], // Eettafel plafondlamp Watt             
                 [ 822, 'Woonkamer',    'SplashEnergyDevice',   null ], // Eettafel plafondlamp Power             
                 [ 824, 'Tuin',         'SplashLightDevice',    null ], // Gevellamp tuin                
    		  	 [ 826, 'Tuin', 		'SplashLightDevice',	null ],	// Gevelelektra tuin    		  	 
                 [ 832, 'Tuin',         'SplashLightDevice',    null ], // Gevellamp tuin                
                 [ 837, 'Tuin',         'SplashLightDevice',    null ], // Tuinkabel                 
                 [ 843, 'Tuin',         'SplashEnergyDevice',   null ], // Tuinkabel kWh                
                 [ 844, 'Tuin',         'SplashEnergyDevice',   null ], // Tuinkabel Watt
                 [ 849, 'Meterkast',    'SplashEnergyDevice',   null ], // Elektra teruglevering vandaag totaal (laag + hoog)
                 [ 850, 'Meterkast',    'SplashEnergyDevice',   null ]  // Elektra teruglevering totaal (laag + hoog)
    			];

		
// Find first occurence of key in object
function getKeyInObject(obj, key) {
	for (var i in obj) {
		if (!obj.hasOwnProperty(i)) continue;
  		if (typeof obj[i] == 'object') {
      		return getKeyInObject(obj[i], key);
   		} else if (i == key) {
       		return obj[i];
   		}
   	}
    return null;
}

const CIRCLIFUL_LIMIT_RED = 15;
const CIRCLIFUL_LIMIT_YELLOW = 30;
const CIRCLIFUL_COLOR_RED = '#d30000';
const CIRCLIFUL_COLOR_YELLOW = '#f4b342';
const CIRCLIFUL_COLOR_GREEN = '#009c00';
const CIRCLIFUL_COLOR_BLUE = '#039cfd';
const CIRCLIFUL_COLOR_GRAY = '#909090';
const CIRCLIFUL_COLOR_BG = '#ebeff2';
const CIRCLIFUL_COLOR_BG_GRAY = '#b0b0b0';

const nl_NL = 0;
const en_US = 1;
const MONTH_STR = [ [ 'Januari', 'Februari', 'Maart', 'April', 'Mei', 'Juni', 'Juli', 'Augustus', 'September', 'Oktober', 'November', 'December' ],	
					[ 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',   'September', 'October', 'November', 'December' ]
					];
function monthToStr( lang, month ) {
	return MONTH_STR[ lang ][ month ];
}
const DAY_STR = [ [ 'Zondag', 'Maandag', 'Dinsdag', 'Woensdag', 'Donderdag', 'Vrijdag', 'Zaterdag' ],	
				  [ 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday' ]
				  ];
function dayToStr( lang, day ) {
	return DAY_STR[ lang ][ day ];
}
const NEATO_MODE_STR = [ [ 'Normaal', 'Eco', 'Turbo' ],	
					     [ 'Regular', 'Eco', 'Turbo' ]
					     ];
function neatoModeToStr( lang, mode ) {
	return NEATO_MODE_STR[ lang ][ mode ];
}

function timestamp( d = null) {
    if ( $.isNumeric( d ) ) {
        d = new Date( d );
    }
    if ( !( d instanceof Date ) ) {
        d = new Date();
    }
	return d.getFullYear() + "-" + (d.getMonth()<10?'0':'') + (d.getMonth()+1) + "-" + (d.getDate()<10?'0':'') + d.getDate() + '.' + (d.getHours()<10?'0':'') + d.getHours() + ":" + (d.getMinutes()<10?'0':'') + d.getMinutes() + "." + (d.getSeconds()<10?'0':'') + d.getSeconds() + '.' + (d.getMilliseconds()<100?'0':'') + (d.getMilliseconds()<10?'0':'') + d.getMilliseconds();
}

function makeId( length ) {
    var text = "";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

    for (var i = 0; i < length; i++)
        text += possible.charAt(Math.floor(Math.random() * possible.length));

    return text;
}


// Convert string to camel case
String.prototype.toUpperCaseFirstChar = function() {
	return this.substr( 0, 1 ).toUpperCase() + this.substr( 1 );
};
String.prototype.toUpperCaseEachWord = function( delim ) {
	delim = delim ? delim : ' ';
	return this.split( delim ).map( function(v) { return v.toUpperCaseFirstChar() } ).join( delim );
};


jQuery(document).ready(function ($) {
	// Handler for .ready() called.
	console.log(timestamp() + " splash.js file load completed");
	try {
		localStorage.setItem( 'SplashPreviousPage', localStorage.getItem('SplashCurrentPage') );
		localStorage.setItem( 'SplashCurrentPage', localStorage.getItem( window.location.href ) );
	} catch(e) {
		console.log(timestamp() + " Could not store location in localStorage.");
	}	
});

// 
function Settings() {
	console.log(timestamp() + ' Settings()');

	// Does the element exist? No: draw, Yes: update
	if ( !$('div#settings-modal').length ) {
		// Does not exist, create it
		var elStr = `<div id="settings-modal" class="modal fade" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true" style="display: none;">
            <div class="modal-dialog modal-lg settings_dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <button type="button" class="close" data-dismiss="modal" aria-hidden="true" style="cursor: pointer;"><i class=" mdi mdi-close"></i></button>
                        <h4 class="modal-title">Splash settings</h4>
                    </div>
                    <div class="modal-body font-13">
                        <div class="row">
                            <div class="col-md-12">
                            <table class="table table-striped">
                                <thead>
                                <tr>
                                    <th class="settings_col_1">#</th>
                                    <th class="settings_col_2">First Name</th>
                                    <th class="settings_col_3">Interval</th>
                                    <th class="settings_col_4">Elements</th>
                                    <th class="settings_col_5">Listeners</th>
                                    <th class="settings_col_6">Events</th>
                                    <th class="settings_col_7"> </th>
                                </tr>
                                </thead>
                                <tbody>
                               <tr id="CentralHSUpdater" class="settings_row">
                                    <td class="settings_col_1" scope="row">1</th>
                                    <td class="settings_col_2">HomeSeer</td>
                                    <td class="settings_col_3 text-right">...</td>
                                    <td class="settings_col_4 text-center">...</td>
                                    <td class="settings_col_5 text-center">...</td>
                                    <td class="settings_col_6 text-center">0</td>
                                    <td class="settings_col_7"><i class="fa fa-lg fa-spin"> </i></th>
                                </tr>                               
                               <tr id="CentralEHUpdater" class="settings_row">
                                    <td class="settings_col_1" scope="row">2</th>
                                    <td class="settings_col_2">Honeywell Evohome</td>
                                    <td class="settings_col_3 text-right">...</td>
                                    <td class="settings_col_4 text-center">...</td>
                                    <td class="settings_col_5 text-center">...</td>
                                    <td class="settings_col_6 text-center">0</td>
                                    <td class="settings_col_7"><i class="fa fa-lg"> </i></th>
                                </tr>
                                <tr id="CentralNRUpdater" class="settings_row">
                                    <td class="settings_col_1" scope="row">3</th>
                                    <td class="settings_col_2">Neato Robotics</td>
                                    <td class="settings_col_3 text-right">...</td>
                                    <td class="settings_col_4 text-center">...</td>
		                            <td class="settings_col_5 text-center">...</td>
									<td class="settings_col_6 text-center">0</td>
                                    <td class="settings_col_7"><i class="fa fa-lg"> </i></th>
                                </tr>
                                <tr id="CentralBoseUpdater" class="settings_row">
                                    <td class="settings_col_1" scope="row">4</th>
                                    <td class="settings_col_2">Bose Updater</td>
                                    <td class="settings_col_3 text-right">...</td>
                                    <td class="settings_col_4 text-center">...</td>
		                            <td class="settings_col_5 text-center">...</td>
                                    <td class="settings_col_6 text-center">0</td>
                                    <td class="settings_col_7"><i class="fa fa-lg"> </i></th>
                               </tr>
                                <tr id="CentralLife360Updater" class="settings_row">
                                    <td class="settings_col_1" scope="row">5</th>
                                    <td class="settings_col_2">Life360</td>
                                    <td class="settings_col_3 text-right">...</td>
                                    <td class="settings_col_4 text-center">...</td>
		                            <td class="settings_col_5 text-center">...</td>
                                    <td class="settings_col_6 text-center">0</td>
                                    <td class="settings_col_7"><i class="fa fa-lg"> </i></th>
                               </tr>
                               <tr id="CentralAudiVehicleUpdater" class="settings_row">
                                    <td class="settings_col_1" scope="row">6</th>
                                    <td class="settings_col_2">myAudi</td>
                                    <td class="settings_col_3 text-right">...</td>
                                    <td class="settings_col_4 text-center">...</td>
                                    <td class="settings_col_5 text-center">...</td>
		                            <td class="settings_col_6 text-center">0</td>
                                    <td class="settings_col_7"><i class="fa fa-lg"> </i></th>
                                </tr>
                               </tbody>
                            </table>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-info waves-effect" data-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div><!-- /.modal -->`;

		$( 'body' ).append( elStr );

		var suh = [ BoseUpdateHandler, EHUpdateHandler, NRUpdateHandler, AudiUpdateHandler, HSUpdateHandler, Life360UpdateHandler ];
		$.each( suh, function( key, handler ) {
			$('tr#' + handler.handlerName + ' td:nth-of-type(7)').on('click', function() {		
				console.log( timestamp() + ' ' + handler.handlerName + ' setting clicked...');
				if ( !CentralSplashUpdater.isDefined( handler.uidt ) ) {
					console.log( timestamp() + ' ignore ' + handler.handlerName + ' click.');
					return;	// Ignore click
				}
				var isRunning = CentralSplashUpdater.isRunning( handler.uidt );
				if ( isRunning ) {
					CentralSplashUpdater.terminate( handler.uidt );
				} else {
					CentralSplashUpdater.restart( handler.uidt );
				};
				isRunning = !isRunning;
				$('tr#' + handler.handlerName + ' td:nth-of-type(7) i').toggleClass( 'fa-play-circle-o', !isRunning );
				$('tr#' + handler.handlerName + ' td:nth-of-type(7) i').toggleClass( 'fa-circle-o-notch', isRunning );
				$('tr#' + handler.handlerName + ' td:nth-of-type(7) i').toggleClass( 'fa-spin', isRunning );
			});
		});

	}
	// Update
	var suh = [ BoseUpdateHandler, EHUpdateHandler, NRUpdateHandler, AudiUpdateHandler, HSUpdateHandler, Life360UpdateHandler ];
	$.each( suh, function( key, handler ) {
		$('tr#' + handler.handlerName + ' td:nth-of-type(3)').html( CentralSplashUpdater.getIntervalStr( handler.uidt ) );
		$('tr#' + handler.handlerName + ' td:nth-of-type(4)').html( CentralSplashUpdater.elementCount( handler.uidt ) );
		$('tr#' + handler.handlerName + ' td:nth-of-type(5)').html( CentralSplashUpdater.callbackCount( handler.uidt ) );
		var isRunning = CentralSplashUpdater.isRunning( handler.uidt );
		$('tr#' + handler.handlerName + ' td:nth-of-type(7) i').toggleClass( 'fa-play-circle-o', !isRunning );
		$('tr#' + handler.handlerName + ' td:nth-of-type(7) i').toggleClass( 'fa-circle-o-notch', isRunning );
		$('tr#' + handler.handlerName + ' td:nth-of-type(7) i').toggleClass( 'fa-spin', isRunning );
		if ( CentralSplashUpdater.callbackCount( handler.uidt ) == 0 ) {
			// No need to start or show play
			$('tr#' + handler.handlerName + ' td:nth-of-type(7) i').addClass('invisible');
		}
	});

	$("#settings-modal").modal();
}
function updateSplashUpdaterSettings( handler, cnt, flash = false ) {
	// Only flash if visible
	$('tr#' + handler.handlerName +' td:nth-of-type(6)').html( cnt );	
	if ( flash && $('div#settings-modal').is(':visible') && $('tr#' + handler.handlerName).css('opacity') == 1 ) {	// Don't start the fading if it is already animating
		$('tr#' + handler.handlerName).fadeOut(50).fadeIn(100);
	}
	if ( $('div#settings-modal').length ) {	// Update settings only if already created
		var isRunning = CentralSplashUpdater.isRunning( handler.uidt );
		$('tr#' + handler.handlerName +' td:nth-of-type(7) i').toggleClass( 'fa-play-circle-o', !isRunning );
		$('tr#' + handler.handlerName +' td:nth-of-type(7) i').toggleClass( 'fa-circle-o-notch', isRunning );
		$('tr#' + handler.handlerName +' td:nth-of-type(7) i').toggleClass( 'fa-spin', isRunning );
	}
}



function SplashLogout( logoutAll = false ) {
	console.log(timestamp() + ' SplashLogout()');

	$.Notification.autoHideNotify('warning', 'top left', 'Loggin out', 'Logging out from Splash!');
	
	// Stop all requests
//	CentralHSUpdater.terminate( true );
//	CentralEHUpdater.terminate( true );
	
	$.ajax({
		type		: 'GET',
		url			: '/aura/logout.php' + ( logoutAll ? '?logoutall=true' : '' ),
		dataType	: 'json',
        encode		: true
	}) // using the done promise callback
	.done(function(data) {
		// log data to the console so we can see
		if ( data.status == "ANON" && data.success == true ) {
			console.log("Logout OK."); 
			$.Notification.autoHideNotify('success', 'top left', 'Logged out', 'Logged out of Splash. Redirecting to login page.');
			window.location = '/aura/login.html';
		} else {
			// here we will handle errors and validation messages
			console.log("Logout FAILED."); 
			$.Notification.autoHideNotify('error', 'top left', 'Logout FAILED!', 'Logging out of Splash failed. Please close your browser to complete logout.');
		}
	})
	.fail(function() {
		$.Notification.notify('error','top left', 'Connection error', 'Could not process logout! Please close your browser to complete logout.');
	})
	.always(function() {
		// Check every 60 seconds
	});

}


// Load temperature devices into element
function loadTemperatureDevice( el, ref, func, type ) {
			
	var jqxhr = $.getJSON( "assets/php/homeseer.getstatus.php?ref=" + ref, function() {
		console.log( "Successful jqxhr request [" + func + "]" );
	})
	.done(function( data ) {
		console.log( data );

		var ref = getKeyInObject( data, 'ref' );
		var name = getKeyInObject( data, 'name' );
		var value = getKeyInObject( data, 'value' );

			if ( ref == 463 ) {	// Smoke sensor
				if ( value > 100 ) { value = 0; }			
			}

		var lastchange = getKeyInObject( data, 'last_change' );	/* /Date(1517243403149)/ */
		// parse
		lastchange = new Date( ( lastchange.substr(6, 13) / 1) );
		var dateOffset = (24*60*60*1000) * 30; // 30 days );
		lastchangeStr = ( monthToStr( nl_NL, lastchange.getMonth() ) ) + " " + lastchange.getDate() + ", " + lastchange.getFullYear();   
		var timeWarning = ( new Date().getTime() - dateOffset > lastchange.getTime() );
    					
		var location = getKeyInObject( data, 'location' );
		var location2 = getKeyInObject( data, 'location2' );
				
		console.log( 'ref: ' + ref + ' name: ' + name + " ( " + value + " ) last change: " + lastchange + " " + lastchangeStr + " (warning=" + timeWarning + ") location: " + location + " location 2: " + location2 );

        $( el ).append('<div class="col-lg-3 col-md-6" id="tempdev'+ref+'"><div class="widget-simple-chart text-right card-box"><div class="circliful-chart" data-dimension="90" data-text="'+value+'%" data-width="5" data-fontsize="14" data-percent="'+value+'" data-fgcolor="'+CIRCLIFUL_COLOR_BLUE+'" data-bgcolor="'+CIRCLIFUL_COLOR_BG+'"></div><div class="wid-icon-info text-right"><p class="text-muted m-b-5 font-13 text-uppercase">'+func+'</p><p class="text-muted m-b-5 font-15">'+type+'</p><h5 class="m-t-0 m-b-5 font-bold"><span>'+location+'</span></h5><h6 class="m-t-0 m-b-5'+(timeWarning?' text-danger':'')+'">Last update: '+lastchangeStr+' <span class="'+(timeWarning?'ion-alert-circled':'')+'"> </span></h6></div></div></div>');
		$('div#tempdev'+ref+' div.circliful-chart').empty().removeData().attr('data-percent', value).attr('data-text', value+'%').attr('data-fgcolor', (value < CIRCLIFUL_LIMIT_RED ? CIRCLIFUL_COLOR_RED : (value < CIRCLIFUL_LIMIT_YELLOW ? CIRCLIFUL_COLOR_YELLOW : CIRCLIFUL_COLOR_GREEN ))).attr('data-bgcolor', (value == 0 ? CIRCLIFUL_COLOR_RED : CIRCLIFUL_COLOR_BG)).circliful()

		console.log( "Successful jqxhr response [" + ref + "]" );
	})
	.fail(function() {
		console.log( "Error retrieving device " + ref );
		$.Notification.notify('error','top left', 'Connection error', 'Could not retrieve data for ' + func + ' [' + ref + '] of type ' + type + '!');
	})
	.always(function() {
		console.log( "Done [" + ref + "]" );
	});
			
	setTimeout(function(){ jqxhr.abort(); }, 3000);

}

// Load temperature devices into element
function loadLightDevice( el, ref, canDim, func, type ) {
	console.log( "function loadLightDevice( \"" + el + "\", \"" + ref + "\", \"" + canDim + "\", \"" + func + "\", \"" + type + "\")" );;
			
	var jqxhr = $.getJSON( "assets/php/homeseer.getstatus.php?ref=" + ref, function() {
		console.log( "Successful getstatus jqxhr request in loadLightDevice() for " + func + " [" + ref + "]" );
	})
	.done(function( data ) {
		console.log( data );

		var ref = getKeyInObject( data, 'ref' );
		var name = getKeyInObject( data, 'name' );
		var value = getKeyInObject( data, 'value' );

		var lastchange = getKeyInObject( data, 'last_change' );	/* /Date(1517243403149)/ */
		// parse
		lastchange = new Date( ( lastchange.substr(6, 13) / 1) );
		var dateOffset = (24*60*60*1000) * 30; // 30 days );
		lastchangeStr = ( monthToStr( nl_NL, lastchange.getMonth() ) ) + " " + lastchange.getDate() + ", " + lastchange.getFullYear();   
		var timeWarning = ( new Date().getTime() - dateOffset > lastchange.getTime() );
    					
		var location = getKeyInObject( data, 'location' );
		var location2 = getKeyInObject( data, 'location2' );
				
		console.log( 'ref: ' + ref + ' name: ' + name + " ( " + value + " ) last change: " + lastchange + " " + lastchangeStr + " (warning=" + timeWarning + ") location: " + location + " location 2: " + location2 );

		if ( canDim ) {
	        $( el ).append('<div class="col-lg-3 col-md-6" id="tempdev'+ref+'"><div id="tempcb'+ref+'" class="widget-simple-chart text-right card-box"><div class="circliful-chart" data-dimension="90" data-text="'+value+'%" data-width="5" data-fontsize="14" data-percent="'+value+'" data-fgcolor="'+CIRCLIFUL_COLOR_BLUE+'" data-bgcolor="'+CIRCLIFUL_COLOR_BG+'"></div><div class="wid-icon-info text-right"><p class="text-muted m-b-5 font-13 text-uppercase">'+name+'</p><p class="text-muted m-b-5 font-15">'+func+'</p><h5 class="m-t-0 m-b-5 font-bold"><span>'+location+'</span></h5><div id="sliderblock_' + ref + '"><input type="text" id="slider_' + ref + '"></div></div></div></div>');
			$('div#tempdev'+ref+' div.circliful-chart').empty().removeData().attr('data-percent', value).attr('data-text', value+'%').circliful()

			// Dimmer, onclick toggle the slider
			$('div#sliderblock_' + ref).slideToggle();	// default slideup
			$('div#tempdev'+ref).click( function(e) {
//				if (!isPaddingClick(this, e)) {
					$('div#sliderblock_' + ref).slideToggle();	// slideUp/ slideDown
//				} else {
//console.log("Padding click");
//				}
			});	// Stop slideup by clicking on the slider
			$('div#sliderblock_' + ref).click(function(event){
				event.stopPropagation();
    		});
/*
    		$('div#tempcb'+ref).click( function(e) {
				if (!isPaddingClick(this, e)) {
					$('div#sliderblock_' + ref).slideToggle();	// slideUp/ slideDown
				} else {
console.log("Padding click");
        		event.stopPropagation();
				}
    		});
  */  		
    		
    		

			// Initialise the slider
			console.log( 'Initialise the slider [' + ref + '] in loadLightDevice()' );

        	var $range = $("#slider_" + ref);          
            $range.ionRangeSlider({
                type: "single",
				grid: true,
                min: 0,
                max: 100,
                hide_min_max: true,
                hide_from_to: false,
                from: value,
                keyboard: true,
                onStart: function (data) {
					console.log('---> Slider ' + ref + ' started');
                },
                onChange: function (data) {
					console.log('---> Slider ' + ref + ' changed to ' + data.from);
			     //   var lrange = $("#slider_" + ref);
			     console.log($(this));
//			     $(this).attr('hide_from_to', false);
//			        $(this).update({
  //                      hide_from_to: false
    //                });
				//	var lslider = lrange.data("ionRangeSlider");
                //    lslider.update({
                //        hide_from_to: false
                //    });

					var jqxhr = $.getJSON( "assets/php/homeseer.controldevicebyvalue.php?user=laemen&pass=domovla&request=controldevicebyvalue&ref=" + ref + "&value=" + data.from, function() {
						console.log( "Successful controldevicebyvalue jqxhr request [" + ref + "]" );
					})
					.done(function( data ) {
						console.log( data );
						console.log( "Successful controldevicebyvalue jqxhr response [" + ref + "]" );
					})
					.fail(function() {
						console.log( "Error retrieving device " + ref );
						$.Notification.notify('error','top left', 'Connection error', 'Could not retrieve data for light [' + ref + ']!');
					})
					.always(function() {
						console.log( "Done [" + ref + "]" );
					});

                },
                onFinish: function (data) {
					console.log('Slider ' + ref + ' finished on ' + data.from);
                },
                onUpdate: function (data) {
					console.log('Slider ' + ref + ' updated');
                }
        	});


		} else {
		}

		console.log( "Successful getstatus jqxhr response in loadLightDevice() for " + func + " [" + ref + "]" );
	})
	.fail(function() {
		console.log( "Error retrieving " + func + " device [" + ref + "] in loadLightDevice()" );
		$.Notification.notify('error','top left', 'Connection error', 'Could not retrieve data for ' + func + ' [' + ref + '] of type ' + type + '!');
	})
	.always(function() {
		console.log( "Done getstatus jqxhr response in loadLightDevice() for " + func + " [" + ref + "]" );
	});
			
	setTimeout(function(){ jqxhr.abort(); }, 3000);

}

function isPaddingClick(element, e) {
	var style = window.getComputedStyle(element, null);
	var pTop = parseInt( style.getPropertyValue('padding-top') );
	var pRight = parseFloat( style.getPropertyValue('padding-right') );
	var pLeft = parseFloat( style.getPropertyValue('padding-left') );  
	var pBottom = parseFloat( style.getPropertyValue('padding-bottom') );
	var width = element.offsetWidth;
	var height = element.offsetHeight;
	var x = parseFloat( e.offsetX );
	var y = parseFloat( e.offsetY );  
console.log( " element.id: " + element.id +
			 " pTop: " + pTop + 
             " pRight: " + pRight +
             " pLeft: " + pLeft +
             " pBottom: " + pBottom +
             " width: " + width +
             " height: " + height +
             " x: " + x +
             " y: " + y +
             " ( x > pLeft && x < width - pRight): " + ( x > pLeft && x < width - pRight) +
             " ( y > pTop && y < height - pBottom): " + ( y > pTop && y < height - pBottom)
             );
	return !(( x > pLeft && x < width - pRight) &&
             ( y > pTop && y < height - pBottom))
}

// ----------------------- Simple Weather Object ------------------------------------------

var simpleWeatherCodes = new Array();
simpleWeatherCodes[0] = [ 0, 'tornado', 'rain' ];
simpleWeatherCodes[1] = [ 1, 'tropical storm', 'rain' ];
simpleWeatherCodes[2] = [ 2, 'hurricane', 'rain' ];
simpleWeatherCodes[3] = [ 3, 'severe thunderstorms', 'rain' ];
simpleWeatherCodes[4] = [ 4, 'thunderstorms', 'rain' ];
simpleWeatherCodes[5] = [ 5, 'mixed rain and snow', 'snow' ];
simpleWeatherCodes[6] = [ 6, 'mixed rain and sleet', 'sleet' ];
simpleWeatherCodes[7] = [ 7, 'mixed snow and sleet', 'snow' ];
simpleWeatherCodes[8] = [ 8, 'freezing drizzle', 'rain' ];
simpleWeatherCodes[9] = [ 9, 'drizzle', 'rain' ];
simpleWeatherCodes[10] = [ 10, 'freezing rain', 'rain' ];
simpleWeatherCodes[11] = [ 11, 'showers', 'rain' ];
simpleWeatherCodes[12] = [ 12, 'showers', 'rain' ];
simpleWeatherCodes[13] = [ 13, 'snow flurries', 'snow' ];
simpleWeatherCodes[14] = [ 14, 'light snow showers', 'snow' ];
simpleWeatherCodes[15] = [ 15, 'blowing snow', 'snow' ];
simpleWeatherCodes[16] = [ 16, 'snow', 'snow' ];
simpleWeatherCodes[17] = [ 17, 'hail', 'rain' ];
simpleWeatherCodes[18] = [ 18, 'sleet', 'sleet' ];
simpleWeatherCodes[19] = [ 19, 'dust', 'fog' ];
simpleWeatherCodes[20] = [ 20, 'foggy', 'fog' ];
simpleWeatherCodes[21] = [ 21, 'haze', 'fog' ];
simpleWeatherCodes[22] = [ 22, 'smoky', 'fog' ];
simpleWeatherCodes[23] = [ 23, 'blustery', 'wind' ];
simpleWeatherCodes[24] = [ 24, 'windy', 'wind' ];
simpleWeatherCodes[25] = [ 25, 'cold', 'clear-day' ];
simpleWeatherCodes[26] = [ 26, 'cloudy', 'cloudy' ];
simpleWeatherCodes[27] = [ 27, 'mostly cloudy (night)', 'partly-cloudy-night' ];
simpleWeatherCodes[28] = [ 28, 'mostly cloudy (day)', 'partly-cloudy-day' ];
simpleWeatherCodes[29] = [ 29, 'partly cloudy (night)', 'partly-cloudy-night' ];
simpleWeatherCodes[30] = [ 30, 'partly cloudy (day)', 'partly-cloudy-day' ];
simpleWeatherCodes[31] = [ 31, 'clear (night)', 'clear-night' ];
simpleWeatherCodes[32] = [ 32, 'sunny', 'clear-day' ];
simpleWeatherCodes[33] = [ 33, 'fair (night)', 'clear-night' ];
simpleWeatherCodes[34] = [ 34, 'fair (day)', 'clear-day' ];
simpleWeatherCodes[35] = [ 35, 'mixed rain and hail', '' ];
simpleWeatherCodes[36] = [ 36, 'hot', 'clear-day' ];
simpleWeatherCodes[37] = [ 37, 'isolated thunderstorms', 'rain' ];
simpleWeatherCodes[38] = [ 38, 'scattered thunderstorms', 'rain' ];
simpleWeatherCodes[39] = [ 39, 'scattered thunderstorms', 'rain' ];
simpleWeatherCodes[40] = [ 40, 'scattered showers', 'rain' ];
simpleWeatherCodes[41] = [ 41, 'heavy snow', 'snow' ];
simpleWeatherCodes[42] = [ 42, 'scattered snow showers', 'snow' ];
simpleWeatherCodes[43] = [ 43, 'heavy snow', 'snow' ];
simpleWeatherCodes[44] = [ 44, 'partly cloudy', 'partly-cloudy-day' ];
simpleWeatherCodes[45] = [ 45, 'thundershowers', 'rain' ];
simpleWeatherCodes[46] = [ 46, 'snow showers', 'snow' ];
simpleWeatherCodes[47] = [ 47, 'isolated thundershowers', 'rain' ];
simpleWeatherCodes[3200] = [ 3200, 'not available', '' ];

function loadWeather(location, woeid, bg) {
	
	/* Does your browser support geolocation? */
	if ("geolocation" in navigator) {
		/* Where in the world are you? */
		navigator.geolocation.getCurrentPosition(
			// Success callback
			function(position) {
			    location = position.coords.latitude + ',' + position.coords.longitude; //load weather using your lat/lng coordinates
			    console.log(timestamp() + " loadWeather() for " + location);
			},
			// error callback
    	    function(err) {
				console.warn(`ERROR(${err.code}): ${err.message}`);
			}, {
			// options
				enableHighAccuracy: true,
				timeout: 10000,
				maximumAge: 0
			}	
		);
	}
    updateWeather( location, woeid, bg );
	setTimeout( function(){ loadWeather(location, woeid, bg) }, 10 * 60 * 1000 );
}
	
function updateWeather(location, woeid, bg) {
    console.log(timestamp() + " updateWeather(" + location + ", " + woeid + " )");
	$.simpleWeather({
	    location: location,
	    woeid: woeid,
//	    unit: 'c,km,mhg,mph',	// mph  "C", distance: "km", pressure: "mb", speed: "km/h"}
	    unit: 'c',	// mph  "C", distance: "km", pressure: "mb", speed: "km/h"}
	    success: function(weather) {
	    	console.log( weather );
	    	// WEATHER WIDGET 2
	    	html =  '<div class="card-box '+bg+'" id="weather_el">';
	    	html += '  <div class="row">';
            html += '    <div class="col-md-7">';
            html += '      <div class="">';
            html += '        <div class="row">';
            html += '          <div class="col-6 text-center">';
            html += '            <canvas id="weather_today" width="115" height="115"></canvas>';
            html += '          </div>';
            html += '          <div class="col-6">';
            html += '            <h2 class="m-t-0 text-white"><b> '+weather.temp+'&deg;'+weather.units.temp+'</b></h2>';
            html += '            <p class="text-white">'+weather.currently+' in '+weather.city+'</p>';
            html += '            <p class="text-white">'+Math.round(weather.wind.speed)+weather.units.speed+' '+weather.wind.direction+' - '+weather.humidity+'%</p>';
            html += '          </div>';
            html += '        </div><!-- end row -->';
            html += '      </div><!-- weather-widget -->';
            html += '    </div>';
            html += '    <div class="col-md-5">';
            html += '      <div class="row">';
            html += '        <div class="wf-day">';
                     
            // weather.forecast[1].image "https://s.yimg.com/zz/combo?a/i/us/nws/weather/gr/5d.png"
            
            html += '          <h4 class="text-white m-t-0" title="'+weather.forecast[1].text+'">'+weather.forecast[1].day+'</h4>';
            html += '          <canvas id="weather_plus1" width="35" height="35"></canvas>';
//            html += '          <img src="'+weather.forecast[1].thumbnail+'" alt="'+weather.forecast[1].text+'" height="35" width="35">';
            html += '          <h4 class="text-white">'+weather.forecast[1].high+'<i class="wi wi-degrees"></i>/ '+weather.forecast[1].low+'<i class="wi wi-degrees"></i></h4>';
            html += '        </div>';
            html += '        <div class="wf-day">';
            html += '          <h4 class="text-white m-t-0" title="'+weather.forecast[2].text+'">'+weather.forecast[2].day+'</h4>';
            html += '          <canvas id="weather_plus2" width="35" height="35"></canvas>';
//            html += '          <img src="'+weather.forecast[2].image+'" alt="'+weather.forecast[2].text+'" height="35" width="35">';
            html += '          <h4 class="text-white">'+weather.forecast[2].high+'<i class="wi wi-degrees"></i>/ '+weather.forecast[2].low+'<i class="wi wi-degrees"></i></h4>';
            html += '        </div>';
            html += '        <div class="wf-day">';
            html += '          <h4 class="text-white m-t-0" title="'+weather.forecast[3].text+'">'+weather.forecast[3].day+'</h4>';
            html += '          <canvas id="weather_plus3" width="35" height="35"></canvas>';
            html += '          <h4 class="text-white">'+weather.forecast[3].high+'<i class="wi wi-degrees"></i>/ '+weather.forecast[3].low+'<i class="wi wi-degrees"></i></h4>';
            html += '        </div>';
            html += '        <div class="wf-day wf-day-4">';
            html += '          <h4 class="text-white m-t-0" title="'+weather.forecast[4].text+'">'+weather.forecast[4].day+'</h4>';
            html += '          <canvas id="weather_plus4" width="35" height="35"></canvas>';
            html += '          <h4 class="text-white">'+weather.forecast[4].high+'<i class="wi wi-degrees"></i>/ '+weather.forecast[4].low+'<i class="wi wi-degrees"></i></h4>';
            html += '        </div>';
            html += '        <div class="wf-day wf-day-5">';
            html += '          <h4 class="text-white m-t-0" title="'+weather.forecast[5].text+'">'+weather.forecast[5].day+'</h4>';
            html += '          <canvas id="weather_plus5" width="35" height="35"></canvas>';
            html += '          <h4 class="text-white">'+weather.forecast[5].high+'<i class="wi wi-degrees"></i>/ '+weather.forecast[5].low+'<i class="wi wi-degrees"></i></h4>';
            html += '        </div>';
            html += '        <div class="wf-day wf-day-6">';
            html += '          <h4 class="text-white m-t-0" title="'+weather.forecast[6].text+'">'+weather.forecast[6].day+'</h4>';
            html += '          <canvas id="weather_plus6" width="35" height="35"></canvas>';
            html += '          <h4 class="text-white">'+weather.forecast[6].high+'<i class="wi wi-degrees"></i>/ '+weather.forecast[6].low+'<i class="wi wi-degrees"></i></h4>';
            html += '        </div>';
            html += '      </div><!-- End row -->';
            html += '    </div> <!-- col-->';
            html += '  </div><!-- End row -->';
            html += '</div><!-- card-box -->';
	      
			$("#weather").html(html);
			//	"clear-day", "clear-night", "partly-cloudy-day", "partly-cloudy-night", "cloudy", "rain", "sleet", "snow", "wind", "fog"
	      
			var icons = new Skycons(
				{"color": "#fff"},
				{"resizeClear": true}
	        );
			// you can add a canvas by it's ID...
			icons.set("weather_today", simpleWeatherCodes[weather.code][2]);
			icons.set("weather_plus1", simpleWeatherCodes[weather.forecast[2].code][2]);
			icons.set("weather_plus2", simpleWeatherCodes[weather.forecast[3].code][2]);
			icons.set("weather_plus3", simpleWeatherCodes[weather.forecast[4].code][2]);
			icons.set("weather_plus4", simpleWeatherCodes[weather.forecast[5].code][2]);
			icons.set("weather_plus5", simpleWeatherCodes[weather.forecast[6].code][2]);
			icons.set("weather_plus6", simpleWeatherCodes[weather.forecast[7].code][2]);
						
            icons.play();

	    },
	    error: function(error) {
	      $("#weather").html('<p>'+error+'</p>');
	    }
	});
}


// ----------------------- Background Updater Object ------------------------------------------
// class for Central updaters
var CentralSplashUpdater = {
    csu: {},
	isDefined: function( uidt ) {
		return ( typeof this.csu[ uidt ] == "object" );
	},
	isRunning: function( uidt ) {
		// Check if there are handles
		var csu = this.csu[ uidt ];
		if ( typeof this.csu[ uidt ] != "object" ) {
			return false;
		}
	   	var isRunning = false;
    	$.each( Object.keys( csu.handles ), function( ei, ev ) {
    		if ( ( typeof csu.handles[ ev ] !== 'undefined' && csu.handles[ ev ] != null ) || 
    			 ( typeof csu.callActive[ ev ] !== 'undefined' && csu.callActive[ ev ] != null ) ) {
    			isRunning = true;
    			return false;	// break from each
    		}
		});
    	return isRunning;
	},
    elementCount: function( uidt ) {
		var csu = this.csu[ uidt ];
		if ( typeof this.csu[ uidt ] != "object" ) {
			return 0;
		}
    	return Object.keys( csu.uids ).length;
    },
    callbackCount: function( uidt ) {
		var csu = this.csu[ uidt ];
		if ( typeof this.csu[ uidt ] != "object" ) {
			return 0;
		}
    	var i = 0;
    	$.each( Object.keys( csu.uids ), function( ei, ev ) {
			i += csu.uids[ev].length;
		});
    	return i;
    },
    getInterval: function( uidt ) {    	
		var csu = this.csu[ uidt ];
		if ( typeof this.csu[ uidt ] != "object" ) {
			return "not set";
		}
		return csu.handler.interval;
    },
    getIntervalStr: function( uidt ) {    				// Fancy interval string
		var csu = this.csu[ uidt ];
		if ( typeof this.csu[ uidt ] != "object" ) {
			return "not set";
		}
		if ( csu.handler.interval > 60500 ) {
			return Math.floor(csu.handler.interval / 60000) + "min " + ( ( csu.handler.interval / 1000 ) - ( Math.floor(csu.handler.interval / 60000) * 60 ) ) + "s";
		}
		return (csu.handler.interval / 1000) + "s";
    },
    getMinInterval: function( uidt ) {
		var csu = this.csu[ uidt ];
		if ( typeof this.csu[ uidt ] != "object" ) {
			return "not set";
		}
    	return csu.handler.minInterval;
    },
    setInterval: function( interval, uidt ) {
		var csu = this.csu[ uidt ];
    	csu.handler.interval = Math.max( interval, csu.handler.minInterval );
    },
    register: function( uid, handler, callback ) {
		var csu = this.csu;
		console.log( timestamp() + " CentralSplashUpdater.register() - registering " + handler.handlerName + " callback for " + uid );
    	if ( !( handler.uidt in csu ) ) {
    		// Init
		   	csu[ handler.uidt ] = {};
		   	csu[ handler.uidt ].uids = {};
		   	csu[ handler.uidt ].handler = handler;		// getUrl, parseData
		   	csu[ handler.uidt ].notifyCnt = 0;			// total events
		    csu[ handler.uidt ].handles = {};			//
		    csu[ handler.uidt ].startTimes = {};
			csu[ handler.uidt ].callActive = {};
			csu[ handler.uidt ].callActiveJSONReq = {};
			csu[ handler.uidt ].notifyCnt = 0;
		}
		csu = this.csu[ handler.uidt ];
		if ( !( uid in csu.uids ) ) {
			// First entry, create array
		   	csu.uids[ uid ] = new Array();
			// Add handler
		   	csu.uids[ uid ].push( callback );
			// // This is a new location, start the updater for it
			CentralSplashUpdater.update( handler.uidt, uid );
    	} else {
			// Else just add handler
		   	csu.uids[ uid ].push( callback );
    	}
    },
	terminate: function( uidt ) {
		var csu = this.csu[ uidt ];
		if ( typeof csu != "object" ) {
			return; 	// Cannot terminate undefined
		};
		var keys = Object.keys( csu.handles );		
		$.each( keys, function( index, key ) {
			clearTimeout( csu.handles[ key ] );
			csu.handles[ key ] = null;
			csu.startTimes[ key ] = null;
			csu.callActive[ key ] = null;
			if ( typeof csu.callActiveJSONReq[ key ] !== 'undefined' && csu.callActiveJSONReq[ key ] != null ) {
				csu.callActiveJSONReq[ key ].abort();
				csu.callActiveJSONReq[ key ] = null;
			}
		});
		updateSplashUpdaterSettings( csu.handler, csu.notifyCnt, false );
	},
	restart: function( uidt ) {
		var csu = this.csu[ uidt ];
		if ( !( uidt in csu ) ) { 
			return; 	// Cannot restart undefined
		};
		var uids = Object.keys( csu.uids );
		$.each( uids, function( index, uid ) {
			// // Restart the updater for it
			CentralSplashUpdater.update( uidt, uid );
		});
		updateSplashUpdaterSettings( csu.handler, csu.notifyCnt, false );
	},
	notify: function ( uidt, obj ) {
		var csu = this.csu[ uidt ];
		console.log( timestamp() + " CentralSplashUpdater.notifier() - calling callbacks for " + obj.getUid() );
		$.each( csu.uids[ obj.getUid() ], function( index, callback ) {
			// Make sure the callback is a function
			if (typeof callback === "function") {
				// Call it, since we have confirmed it is callable
				callback( obj );
			}
		});
		updateSplashUpdaterSettings( csu.handler, csu.notifyCnt, false );
    },
    update: function ( uidt, uid ) {				// can be called on intervals, or just to initiate a new update now
		var csu = this.csu[ uidt ];
    	// If an update is active, ignore this
    	if ( typeof csu.callActive[ uid ] !== 'undefined' && csu.callActive[ uid ] != null ) {
    		console.log( timestamp() + " CentralSplashUpdater.update() called for " + uid + " ignored, request in progress...");
    		return;
		}
    	// If an update is scheduled, cancel that one and use this one now. Cannot distinhguish between timeer of user request, just abort existing timeouts
    	if ( typeof csu.handles[ uid ] !== 'undefined' && csu.handles[ uid ] != null ) {
			clearTimeout( csu.handles[ uid ] );
		}    	
		csu.handles[ uid ] = null;
		csu.startTimes[ uid ] = null;
		csu.callActive[ uid ] = true;
		updateSplashUpdaterSettings( csu.handler, ++csu.notifyCnt, true );
		csu.callActiveJSONReq = $.getJSON( csu.handler.getUrl( uid ), function() {
			console.log( timestamp() + " CentralSplashUpdater.update() - Successful request for " + uid );
			csu.callActive[ uid ] = this;
			updateSplashUpdaterSettings( csu.handler, csu.notifyCnt, false );
		})
		.done(function( data ) {
			console.log( timestamp() + " CentralSplashUpdater.update() - Successful response for " + uid );

			// Parse and notify
			csu.handler.parseData( uid, data );
		})
		.fail(function( jqxhr, textStatus, error ) {
			console.log( timestamp() + ' CentralSplashUpdater.update() - Error retrieving data for ' + csu.handler.handlerName + ' with uid ' + uid + ". " + textStatus + ", " + error );
			$.Notification.notify('error','top left', 'Connection error', 'Could not retrieve data for ' + csu.handler.handlerName + '!' );
		})
		.always(function() {
			console.log( timestamp() + " CentralSplashUpdater.update() - Done " + uid + ", again in " + CentralSplashUpdater.getInterval( uidt ) );
			// Update again in x seconds
			if ( this == csu.callActive[ uid ] ) {
				csu.handles[ uid ] = setTimeout( function() { CentralSplashUpdater.update( uidt, uid ) }, CentralSplashUpdater.getInterval( uidt ) );
				csu.startTimes[ uid ] = new Date();
				csu.callActive[ uid ] = null;
				csu.callActiveJSONReq[ uid ] = null;
			}
			updateSplashUpdaterSettings( csu.handler, csu.notifyCnt, false );
		});
    }
}


var NRUpdateHandler = {
	handlerName: 'CentralNRUpdater',
	uidt: 'neato',
    interval: 60000,	// Use 1 minute
    minInterval: 10000,	// Do not accept less than 10 seconds
    getUrl: function ( uid ) {
		return "assets/php/neato.getstatus.php";	// For this ignore the identifier
	},
	parseData: function ( uid, data ) {
		console.log( timestamp() + " NRUpdateHandler.parseData()" );

		$.each( data.robots, function( index, robotData ) {
			// Pass robot info
			var robot = NeatoRoboticsFactory.create( robotData.serial );

			robot.setName( robotData.name );
			robot.setModel( robotData.model );
			robot.setSecret( robotData.secret );
			robot.setCharging( robotData.isCharging );
			robot.setDocked( robotData.isDocked );
			robot.setError( robotData.isError );
			robot.setErrorString( robotData.error );
			robot.setScheduleEnabled( robotData.isScheduleEnabled );
			robot.setCharge( robotData.charge );
			robot.setFirmware( robotData.firmware );
			robot.setLatestFirmware( robotData.latestFirmware );
			robot.setSchedule( robotData.schedule );				
			robot.setState( robotData.state );				
			robot.setAction( robotData.action );				
			robot.setAvailableCommands( robotData.availableCommands );				

			// Now notify the callbacks
			CentralSplashUpdater.notify( NRUpdateHandler.uidt, robot );
		});
	}
};



var EHUpdateHandler = {
	handlerName: 'CentralEHUpdater',
	uidt: 'evohome',
    interval: 60000,	// Use 1 minute
    minInterval: 10000,	// Do not accept less than 10 seconds
    getUrl: function ( uid ) {
		return "assets/php/evohome.getstatus.php";	// For this ignore the identifier
	},
	parseData: function ( locationId, data ) {		// uid is the locationId
		console.log( timestamp() + " EHUpdateHandler.parseData()" );

		var locationObj = EHLocationFactory.create( locationId );
		locationObj.setGatewayId( getKeyInObject( data, 'gatewayId' ) );
		locationObj.setSystemType( getKeyInObject( data, 'systemType' ) );
		locationObj.setSystemId( getKeyInObject( data, 'systemId' ) );
		locationObj.setMode( getKeyInObject( data, 'mode' ) );
		locationObj.setPermanent( getKeyInObject( data, 'isPermanent' ) === true );

		$.each( data.zones, function( index, zoneData ) {
			// Pass zone info
			var zoneId = getKeyInObject( zoneData, 'zoneId' );
			var zone = locationObj.getZone( zoneId );
			zone.setName( getKeyInObject( zoneData, 'name' ) );
			zone.setTemperature( getKeyInObject( zoneData, 'temperature' ) );
			zone.setAvailable( getKeyInObject( zoneData, 'isAvailable' ) === true );
			zone.setTargetTemperature( getKeyInObject( zoneData, 'targetTemperature' ) );
			zone.setSetpointMode( getKeyInObject( zoneData, 'setpointMode' ) );
		});
		
		// Now notify the callbacks
		CentralSplashUpdater.notify( EHUpdateHandler.uidt, locationObj );
	}
};


var BoseUpdateHandler = {
	handlerName: 'CentralBoseUpdater',
	uidt: 'bose',
    interval: 61000,	// Use 1 minute
    minInterval: 10000,	// Do not accept less than 10 seconds
    getUrl: function ( uid ) {
		return "assets/php/bose.getstatus.php?ip=" + uid;
	},
	parseData: function ( uid, data ) {
		console.log( timestamp() + " BoseUpdateHandler.parseData()" );

		var soundTouch = SoundTouchFactory.create( data.ip );
		soundTouch.setName( data.name );
		soundTouch.setType( data.type );
		soundTouch.setVolume( data.volume );
		soundTouch.setMuted( data.muted );
		soundTouch.setPresets( data.presets );
		soundTouch.setNowPlaying( data.nowPlaying );

		// Now notify the callbacks
		CentralSplashUpdater.notify( BoseUpdateHandler.uidt, soundTouch );
	}
};

var HSUpdateHandler = {
	handlerName: 'CentralHSUpdater',
	uidt: 'homeseer',
    interval: 5000,	// Use 1 minute
    minInterval: 5000,	// Do not accept less than 10 seconds
    getUrl: function ( uid ) {
		return "assets/php/homeseer.getstatus.php?ref=" + uid;
	},
	parseData: function ( uid, data ) {
		console.log( timestamp() + " HSUpdateHandler.parseData() - for ref " + uid );

		var ref = getKeyInObject( data, 'ref' );

		var hsDev = HSDeviceFactory.create( ref );
		hsDev.setName( getKeyInObject( data, 'name' ) );
		hsDev.setValue( getKeyInObject( data, 'value' ) );
		if ( ref == 463 ) {	// Smoke sensor
			if ( hsDev.getValue() > 100 ) { hsDev.setValue( 0 ); }			
		}
		hsDev.setStatus( getKeyInObject( data, 'status' ) );
		hsDev.setLastChangeHS( getKeyInObject( data, 'last_change' ) );	// /Date(1517243403149)/ will be parsed
		hsDev.setLocation( getKeyInObject( data, 'location' ) );
		hsDev.setLocation2( getKeyInObject( data, 'location2' ) );
		hsDev.setType( getKeyInObject( data, 'device_type_string' ) );

		// Now notify the callbacks
		CentralSplashUpdater.notify( HSUpdateHandler.uidt, hsDev );
	}
};

var HSGraphDataUpdateHandler = {
    handlerName: 'CentralHSGraphDataUpdater',
    uidt: 'flot',
    interval: 300000, // Use 5 minute
    minInterval: 60000,  // Do not accept less than 1 mniute
    getUrl: function ( uid ) {
        return "assets/php/flot/lastweek.php?id=" + uid;
    },
    parseData: function ( uid, data ) {
        console.log( timestamp() + " HSGraphDataUpdateHandler.parseData() - for ref " + uid );

        var graphData = HSGraphDataDeviceFactory.create( data.id );
        graphData.setType( data.type );
        graphData.setData( data.data );
        graphData.setMin( data.min );
        graphData.setMax( data.max );

        // Now notify the callbacks
        CentralSplashUpdater.notify( HSGraphDataUpdateHandler.uidt, graphData );
    }
};


var AudiUpdateHandler = {
	handlerName: 'CentralAudiVehicleUpdater',
	uidt: 'audi',
    interval: 60000,	// Use 1 minute
    minInterval: 5000,	// Do not accept less than 10 seconds
    getUrl: function ( uid ) {
		return "assets/php/audi.getstatus.php";					// ignore uid
	},
	parseData: function ( uid, data ) {
		console.log( timestamp() + " AudiUpdateHandler.parseData()" );

		$.each( data.userVehicles, function( index, vehicleData ) {
			var vehicle = AudiVehicleFactory.create( vehicleData.vin );
			vehicle.setLatitude( vehicleData.latitude );
			vehicle.setLongitude( vehicleData.longitude );
			vehicle.setTimestampCarCaptured( vehicleData.timestampCarCaptured );	// 2018-03-19T19:56:18
			vehicle.setTimestampCarSent( vehicleData.timestampCarSent );			// 2018-03-19T19:56:18
			vehicle.setTimestampCarSentUTC( vehicleData.timestampCarSentUTC );	// 2018-03-19T18:55:22Z
			vehicle.setParkingTimeUTC( vehicleData.parkingTimeUTC );				// 2018-03-19T18:55:22Z

			// Now notify the callbacks
			CentralSplashUpdater.notify( AudiUpdateHandler.uidt, vehicle );
		});

	}
};

var Life360UpdateHandler = {
	handlerName: 'CentralLife360Updater',
	uidt: 'life360',
    interval: 60000,	// Use 1 minute
    minInterval: 5000,	// Do not accept less than 10 seconds
    getUrl: function ( uid ) {
		return "assets/php/life360.getstatus.php";					// ignore uid
	},
	parseData: function ( uid, data ) {
		console.log( timestamp() + " Life360UpdateHandler.parseData()" );

		$.each( data.circles, function( index, circleData ) {
			$.each( circleData.member, function( index, memberData ) {
				var member = Life360MemberFactory.create( memberData.id );
				member.setLatitude( memberData.location.latitude );
				member.setLongitude( memberData.location.longitude );
				member.setAccuracy( memberData.location.accuracy );
				member.setSince( memberData.location.since );
				member.setTimestamp( memberData.location.timestamp );	
				member.setBattery( memberData.battery );
				member.setCharging( memberData.charge );
				member.setFirstname( memberData.firstName );
				member.setLastname( memberData.lastName );
				member.setAvatar( memberData.avatar );
				member.setWifi( memberData.wifiState );

				// Now notify the callbacks
				CentralSplashUpdater.notify( Life360UpdateHandler.uidt, member );
			});
		});
	}
};

var OmnikPortalUpdateHandler = {
    handlerName: 'CentralOmnikPortalUpdater',
    uidt: 'omnikportal',
    interval: 60000,    // Use 1 minute
    minInterval: 5000,  // Do not accept less than 10 seconds
    getUrl: function ( uid ) {
        return "assets/php/omnikportal.getstatus.php";                  // ignore uid
    },
    parseData: function ( uid, data ) {
        console.log( timestamp() + " OmnikPortalUpdateHandler.parseData()" );

        var omnikPortal = OmnikPortalFactory.create( );
        omnikPortal.setNowPower( data.omnikportal.nowPower );
        omnikPortal.setNowPowerUnit( data.omnikportal.nowPowerUnit );
        omnikPortal.setDayPower ( data.omnikportal.dayPower );
        omnikPortal.setDayPowerUnit( data.omnikportal.dayPowerUnit );
        omnikPortal.setMonthPower( data.omnikportal.monthPower );
        omnikPortal.setMonthPowerUnit( data.omnikportal.monthPowerUnit );
        omnikPortal.setYearPower( data.omnikportal.yearPower );
        omnikPortal.setYearPowerUnit( data.omnikportal.yearPowerUnit );
        omnikPortal.setAllPower( data.omnikportal.allPower );
        omnikPortal.setAllPowerUnit ( data.omnikportal.allPowerUnit );
        omnikPortal.setPeakPower( data.omnikportal.peakPower );
        omnikPortal.setPeakPowerUnit( data.omnikportal.peakPowerUnit );

        // Now notify the callbacks
        CentralSplashUpdater.notify( OmnikPortalUpdateHandler.uidt, omnikPortal );

    }
};


// ----------------------- HomeSeer Object ------------------------------------------

// Represents a HomeSeer device
function HSDevice ( ref ) {
    this.ref = ref;
    this.name = null;
    this.value = null;	// numeric
    this.status = null;	// string
    this.lastChange = null;
    this.location = null;
    this.location2 = null;
    this.type = HSDevice.HSDT_UNKNOWN;
    this.typeStr = "";
}

HSDevice.HSDT_UNKNOWN = 0;
HSDevice.HSDT_SWITCH = 1;
HSDevice.HSDT_DIMMER = 2;
HSDevice.HSDT_SENSOR = 3;
HSDevice.HSDT_MULTI = 4;

HSDevice.prototype.getUid = function() {				// To comply with CentralSplashUpdater
    return this.ref;
};
HSDevice.prototype.getValue = function() {
    var value = this.value;
    if ( value == null ) { return 0; }
    if ( value == 0 ) { return 0; }
    if ( value < 1 && value > 0 ) { return (Math.round(value *100) /100).toFixed(3); }
    if ( value >= 1 && value < 100 ) {
        if ( (Math.round(value * 10) /10).toFixed(1) != Math.round(value) ) return (Math.round(value * 10) /10).toFixed(1);
        return value;
    }
    if ( value >= 100 ) {
        return Math.round(value); 
    }
    return value;
};
HSDevice.prototype.getUnit = function() {
    if ( ( !this.status ) || typeof this.status != "string" )  return '';
    if ( this.status.includes("kWh") ) { return 'kWh'; }
    if ( this.status.includes("kW") ) { return 'kW'; }
    if ( this.status.includes("W") ) { return 'W'; }
    if ( this.status.includes("%") ) { return '%'; }
    return '';
};
HSDevice.prototype.getHandler = function() {
    return HSUpdateHandler;
};

HSDevice.prototype.getEnergy = function() {
    return this.getValue();
};
HSDevice.prototype.getEnergyUnit = function() {
    return this.getUnit();
};
HSDevice.prototype.getRef = function() {
    return this.ref;
};
HSDevice.prototype.getName = function() {
    return this.name;
};
HSDevice.prototype.setName = function( name ) {
    this.name = name;
};
HSDevice.prototype.setValue = function( value ) {
    this.value = value;
};
HSDevice.prototype.getStatus = function() {
    return this.status;
};
HSDevice.prototype.setStatus = function( status ) {
    this.status = status;
};
HSDevice.prototype.isOff = function() {
    return ( this.value == null || this.value === 'undefined' || this.value == 0 );
};
HSDevice.prototype.getLastChange = function() {
    return this.lastChange;
};
HSDevice.prototype.getLastChangeStr = function() {
	if ( !( this.lastChange instanceof Date ) ) {
		return "---";
	}
	return this.lastChange.getDate()  + " " + monthToStr( nl_NL, this.lastChange.getMonth() ) + ", " + this.lastChange.getFullYear();   
};
HSDevice.prototype.getLastChangeWithTimeHtml = function() {
	if ( !( this.lastChange instanceof Date ) ) {
		return "---";
	}
	return "<i class=\"fa fa-calendar\"></i> " + this.lastChange.getDate()  + " " + monthToStr( nl_NL, this.lastChange.getMonth() ) + ", " + this.lastChange.getFullYear() + " <i class=\"fa fa-clock-o\"></i> " + this.lastChange.getHours() + ":" + (this.lastChange.getMinutes()<10?'0':'') + this.lastChange.getMinutes() + "." + (this.lastChange.getSeconds()<10?'0':'') + this.lastChange.getSeconds();
}
/* Set lastChange in HS format /Date(1517243403149)/ */
HSDevice.prototype.setLastChangeHS = function( lastChangeHS ) {
	/* /Date(1517243403149)/ */
	this.lastChange = new Date( ( lastChangeHS.substr(6, 13) / 1) );
};
/* Set lastChange in JS Date format */
HSDevice.prototype.setLastChange = function( lastChange ) {
	this.lastChange = lastChange;
};
HSDevice.prototype.getLocation = function() {
    return this.location;
};
HSDevice.prototype.setLocation = function( location ) {
    this.location = location;
};
HSDevice.prototype.getLocation2 = function() {
    return this.location2;
};
HSDevice.prototype.setLocation2 = function( location2 ) {
    this.location2 = location2;
};
HSDevice.prototype.canDim = function() {
	console.log( timestamp() + " HSDevice.canDim() ["+this.ref+"] - type: " + this.type + " return: " + ( this.type == HSDevice.HSDT_DIMMER ) );
	" + type + " 
    return ( this.type == HSDevice.HSDT_DIMMER );
};
HSDevice.prototype.canSwitch = function() {
    return ( this.type == HSDevice.HSDT_SWITCH || this.type == HSDevice.HSDT_DIMMER );
};
HSDevice.prototype.isSwitch = function() {
    return this.type == HSDevice.HSDT_SWITCH;
};
HSDevice.prototype.setType = function( type ) {
	console.log( timestamp() + " HSDevice.setType( " + type + " ) ["+this.ref+"]");
	if ( typeof type == "string") {
		// Parse
		switch(type) {
		    case "Z-Wave Switch Binary":
				console.log( timestamp() + " HSDevice.setType( " + type + " ) ["+this.ref+"] - set to switch");
				this.setType( HSDevice.HSDT_SWITCH );
	        	break;
		    case "Z-Wave Switch Multilevel":
				console.log( timestamp() + " HSDevice.setType( " + type + " ) ["+this.ref+"] - set to dimmer");
				this.setType( HSDevice.HSDT_DIMMER );
	        	break;
			default:
		}
		return;
	}
	if ( typeof type == "number" ) {
		// assign
		console.log( timestamp() + " HSDevice.setType( " + type + " ) ["+this.ref+"] - set to " + type);
		this.type = type;
		switch ( type ) {
			case HSDevice.HSDT_SWITCH:
				this.typeStr = "Switch";
				break;
			case HSDevice.HSDT_DIMMER:	
				this.typeStr = "Dimmer";
				break;
			case HSDevice.HSDT_SENSOR:	
				this.typeStr = "Sensor";
				break;
			case HSDevice.HSDT_MULTI:	
				this.typeStr = "Multi";
				break;
			case HSDevice.HSDT_UNKNOWN:	
				this.typeStr = "";
			default:
		}
		return;
	}
};
HSDevice.prototype.getTypeStr = function() {
    return this.typeStr;
};

HSDevice.HSDT_UNKNOWN = 0;
HSDevice.HSDT_SWITCH = 1;
HSDevice.HSDT_DIMMER = 2;
HSDevice.HSDT_SENSOR = 3;
HSDevice.HSDT_MULTI = 4;


// ----------------------- Bose SoundTouch ------------------------------------------

// Represents an Evohome location
function SoundTouch ( ip ) {
    this.ip = ip;
	this.name = "";
	this.type = "";
	this.volume = 0;
	this.mute = false;
	this.presets = [];
	this.nowPlaying = [];
}
SoundTouch.prototype.getUid = function() {			// Interface for the CentralSplashUpdater
    return this.ip;
};
SoundTouch.prototype.getValue = function() {
    return this.getVolume();
};
SoundTouch.prototype.getHandler = function() {
    return BoseUpdateHandler;
};
SoundTouch.prototype.getIP = function() {
    return this.ip;
};
SoundTouch.prototype.getName = function() {
    return this.name;
};
SoundTouch.prototype.setName = function( name ) {
    this.name = name;
};
SoundTouch.prototype.getType = function() {
    return this.type;
};
SoundTouch.prototype.setType = function( type ) {
    this.type = type;
};
SoundTouch.prototype.getVolume = function() {
    return this.volume;
};
SoundTouch.prototype.setVolume = function( volume ) {
    this.volume = volume;
};
SoundTouch.prototype.isMuted = function() {
    return this.mute;
};
SoundTouch.prototype.setMuted = function( muted ) {
    this.mute = muted;
};
SoundTouch.prototype.getPresets = function() {
    return this.presets;
};
SoundTouch.prototype.setPresets = function( presets ) {
    this.presets = presets;
};
SoundTouch.prototype.getNowPlaying = function() {
    return this.nowPlaying;
};
SoundTouch.prototype.setNowPlaying = function( nowPlaying ) {
    this.nowPlaying = nowPlaying;
};
SoundTouch.prototype.getNowPlayingStatusString = function( ) {
	if ( this.nowPlaying === 'undefined' || this.nowPlaying.source === 'undefined' || typeof this.nowPlaying.source != 'string' ) {
		return "...";
	}
	this.nowPlaying.source = this.nowPlaying.source.replace(/_/g, " ");
	return this.nowPlaying.source.toLowerCase().toUpperCaseEachWord(" ");
};
SoundTouch.prototype.getNowPlayingStatusHtml = function( ) {
	var str = this.getNowPlayingStatusString();
	
	if ( str == "Notification" && this.nowPlaying.playStatus !== 'undefined' && typeof this.nowPlaying.playStatus == 'string' ) {
		switch ( this.nowPlaying.playStatus ) {
			case "PLAY_STATE":
				return '<i class="fa fa-bullhorn" style="color: #ff0000 !important"><span class="text-light"> Playing</span></i>';
			case "PAUSE_STATE":
				return '<i class="fa fa-bullhorn" style="color: #ff0000 !important"><span class="text-light"> Paused</span></i>';
			case "STOP_STATE":
				return '<i class="fa fa-bullhorn" style="color: #ff0000 !important"><span class="text-light"> Stopped</span></i>';
			case "BUFFERING_STATE":
				return '<i class="fa fa-bullhorn" style="color: #ff0000 !important"><span class="text-light"> Buffering</span></i>';
		}
	}
	if ( str == "Internet Radio" && this.nowPlaying.playStatus !== 'undefined' && typeof this.nowPlaying.playStatus == 'string' ) {
		switch ( this.nowPlaying.playStatus ) {
			case "PLAY_STATE":
				return '<i class="fa fa-mixcloud" style="color: #d442f4 !important"><span class="text-light"> Playing</span></i>';
			case "PAUSE_STATE":
				return '<i class="fa fa-mixcloud" style="color: #d442f4 !important"><span class="text-light"> Paused</span></i>';
			case "STOP_STATE":
				return '<i class="fa fa-mixcloud" style="color: #d442f4 !important"><span class="text-light"> Stopped</span></i>';
			case "BUFFERING_STATE":
				return '<i class="fa fa-mixcloud" style="color: #d442f4 !important"><span class="text-light"> Buffering</span></i>';
		}
	}
	// TODO INTERNET_RADIO
	if ( str == "Spotify" && this.nowPlaying.playStatus !== 'undefined' && typeof this.nowPlaying.playStatus == 'string' ) {
		switch ( this.nowPlaying.playStatus ) {
			case "PLAY_STATE":
				return '<i class="fa fa-spotify" style="color: #1db954 !important"><span class="text-light"> Playing</span></i>';
			case "PAUSE_STATE":
				return '<i class="fa fa-spotify" style="color: #1db954 !important"><span class="text-light"> Paused</span></i>';
			case "STOP_STATE":
				return '<i class="fa fa-spotify" style="color: #1db954 !important"><span class="text-light"> Stopped</span></i>';
			case "BUFFERING_STATE":
				return '<i class="fa fa-spotify" style="color: #1db954 !important"><span class="text-light"> Buffering</span></i>';
		}
	}
	if ( str == "Aux" ) {
		// Down't know the play state
		return '<i class="fa fa-bluetooth-b" style="color: #0088cc !important"><span class="text-light"> AUX</span></i>';
	}
	return str;
};
SoundTouch.prototype.isRepeatEnabled = function( ) {
	if ( this.nowPlaying === 'undefined' || this.nowPlaying.repeat === 'undefined' || ( typeof this.nowPlaying.repeat != 'string' && typeof this.nowPlaying.repeat != 'boolean' ) ) {
		return false;
	}
	return ( this.nowPlaying.repeat === 'true' || this.nowPlaying.repeat == true );
};
SoundTouch.prototype.isShuffleEnabled = function( ) {
	if ( this.nowPlaying === 'undefined' || this.nowPlaying.shuffle === 'undefined' || ( typeof this.nowPlaying.shuffle != 'string' && typeof this.nowPlaying.shuffle != 'boolean' ) ) {
		return false;
	}
	return ( this.nowPlaying.shuffle === 'true' || this.nowPlaying.shuffle == true );
};
SoundTouch.prototype.isSkipEnabled = function( ) {
	if ( this.nowPlaying === 'undefined' || this.nowPlaying.skipEnabled === 'undefined' || ( typeof this.nowPlaying.skipEnabled != 'string' && typeof this.nowPlaying.skipEnabled != 'boolean' ) ) {
		return false;
	}
	return ( this.nowPlaying.skipEnabled === 'true' || this.nowPlaying.skipEnabled == true );
};
SoundTouch.prototype.isSkipPreviousEnabled = function( ) {
	if ( this.nowPlaying === 'undefined' || this.nowPlaying.skipPreviousEnabled === 'undefined' || ( typeof this.nowPlaying.skipPreviousEnabled != 'string' && typeof this.nowPlaying.skipPreviousEnabled != 'boolean' ) ) {
		return false;
	}
	return ( this.nowPlaying.skipPreviousEnabled === 'true' || this.nowPlaying.skipPreviousEnabled == true );
};
SoundTouch.prototype.getPlayStatus = function( ) {
	if ( this.nowPlaying === 'undefined' || this.nowPlaying.playStatus === 'undefined' || typeof this.nowPlaying.playStatus != 'string' ) {
		return 'UNKNOWN';
	}
	return this.nowPlaying.playStatus;
};
SoundTouch.prototype.isPlaying = function( ) {
	if ( this.nowPlaying === 'undefined' || this.nowPlaying.playStatus === 'undefined' || typeof this.nowPlaying.playStatus != 'string' ) {
		return false;
	}
	return ( this.nowPlaying.playStatus == 'PLAY_STATE' );
};
SoundTouch.prototype.isPaused = function( ) {
	if ( this.nowPlaying === 'undefined' || this.nowPlaying.playStatus === 'undefined' || typeof this.nowPlaying.playStatus != 'string' ) {
		return false;
	}
	return ( this.nowPlaying.playStatus == 'PAUSE_STATE' );
};
SoundTouch.prototype.isStopped = function( ) {
	if ( this.nowPlaying === 'undefined' || this.nowPlaying.playStatus === 'undefined' || typeof this.nowPlaying.playStatus != 'string' ) {
		return false;
	}
	return ( this.nowPlaying.playStatus == 'STOP_STATE' );
};
SoundTouch.prototype.getStationName = function( ) {
	if ( this.nowPlaying === 'undefined' || this.nowPlaying.stationName === 'undefined' || typeof this.nowPlaying.stationName != 'string' ) {
		return '';
	}
	return this.nowPlaying.stationName;
};
SoundTouch.prototype.getDescription = function( ) {
	if ( this.nowPlaying === 'undefined' || this.nowPlaying.description === 'undefined' || typeof this.nowPlaying.description != 'string' ) {
		return '';
	}
	return this.nowPlaying.description;
};
SoundTouch.prototype.getStationLocation = function( ) {
	if ( this.nowPlaying === 'undefined' || this.nowPlaying.stationLocation === 'undefined' || typeof this.nowPlaying.stationLocation != 'string' ) {
		return '';
	}
	return this.nowPlaying.stationLocation;
};
SoundTouch.prototype.getItemName = function( ) {
	if ( this.nowPlaying === 'undefined' || this.nowPlaying.itemName === 'undefined' || typeof this.nowPlaying.itemName != 'string' ) {
		return '';
	}
	return this.nowPlaying.itemName;
};
SoundTouch.prototype.getArtist = function( ) {
	if ( this.nowPlaying === 'undefined' || this.nowPlaying.artist === 'undefined' || typeof this.nowPlaying.artist != 'string' ) {
		return '';
	}
	return this.nowPlaying.artist;
};
SoundTouch.prototype.getTrack = function( ) {
	if ( this.nowPlaying === 'undefined' || this.nowPlaying.track === 'undefined' || typeof this.nowPlaying.track != 'string' ) {
		return '';
	}
	return this.nowPlaying.track;
};
SoundTouch.prototype.getAlbum = function( ) {
	if ( this.nowPlaying === 'undefined' || this.nowPlaying.album === 'undefined' || typeof this.nowPlaying.album != 'string' ) {
		return '';
	}
	return this.nowPlaying.album;
};
SoundTouch.prototype.getArt = function( ) {
	if ( this.nowPlaying === 'undefined' || this.nowPlaying.itemName === 'undefined' || typeof this.nowPlaying.itemName != 'string' ) {
		return "/assets/images/Bose_logo.png";
	}
	// First check if there is art in the Now Playing section
	if ( this.nowPlaying.art !== 'undefined' && typeof this.nowPlaying.art == 'string' && this.nowPlaying.art.length > 0 )  {
		// There is, return it
		return this.nowPlaying.art;
	}
	// check if a preset exists
	var soundTouch = this;
	var art = null;
	$.each( this.getPresets(), function( index, preset ) {
		if ( preset.itemName == soundTouch.getItemName() ) {
			// Use this art - strangely we cannot return the value, down't return the function!
			art = preset.containerArt;
			return false;	// Break from the each loop
		}
	});
	if ( art != null && art.length != 0 ) return art;
	// Not in there, Spotify?
	if ( this.getNowPlayingStatusString() == "Spotify" ) {
		// use Spotify logo
		return "/assets/images/spotify-logo.png";
	}
	return "/assets/images/Bose_logo.png";
};
SoundTouch.prototype.getPlaylist = function( ) {
	var str = this.getNowPlayingStatusString();
	if ( str != "Spotify" || this.nowPlaying.itemName === 'undefined' || typeof this.nowPlaying.itemName != 'string' || this.nowPlaying.itemName.length == 0 ) {
		return "";
	}
	return this.nowPlaying.itemName;
};
SoundTouch.prototype.isPlaylist = function( ) {
	var str = this.getPlaylist();
	return ( str.length != 0 );
};

// ----------------------- Neato Robot ------------------------------------------

// Represents an Neato robot
function NeatoRobot ( serial ) {
    this.serial = serial;
    this.name = '';
    this.model = '';
    this.secret = '';
    this.charging = false;
    this.docked = false;
    this.error = false;
    this.errorString = '';
    this.scheduleEnabled = false;
    this.charge = 0;
    this.firmware = '';
    this.latestFirmware = '';
	this.schedule = [];
    this.state = 0;
    this.action = 0;
    this.availableCommands = [];
}
NeatoRobot.prototype.getUid = function() {			// Interface for the CentralSplashUpdater
    return this.getSerial();
};
NeatoRobot.prototype.getValue = function() {
    return this.getState();
};
NeatoRobot.prototype.getHandler = function() {
    return NeatoUpdateHandler;
};
NeatoRobot.prototype.getSerial = function() {
    return this.serial;
};
NeatoRobot.prototype.getName = function() {
    return this.name;
};
NeatoRobot.prototype.setName = function( name ) {
    this.name = name;
};
NeatoRobot.prototype.getModel = function() {
    return this.model;
};
NeatoRobot.prototype.setModel = function( model ) {
    this.model = model;
};
NeatoRobot.prototype.getSecret = function() {
    return this.secret;
};
NeatoRobot.prototype.setSecret = function( secret ) {
    this.secret = secret;
};
NeatoRobot.prototype.isCharging = function() {
    return this.charging;
};
NeatoRobot.prototype.setCharging = function( charging ) {
    this.charging = charging;
};
NeatoRobot.prototype.isDocked = function() {
    return this.docked;
};
NeatoRobot.prototype.setDocked = function( docked ) {
    this.docked = docked;
};
NeatoRobot.prototype.isError = function() {
    return this.error;
};
NeatoRobot.prototype.setError = function( error ) {
    this.error = error;
};
NeatoRobot.prototype.getErrorString = function() {
    return this.errorString;
};
NeatoRobot.prototype.setErrorString = function( errorString ) {
    this.errorString = errorString;
};
NeatoRobot.prototype.isScheduleEnabled = function() {
    return this.scheduleEnabled;
};
NeatoRobot.prototype.setScheduleEnabled = function( scheduleEnabled ) {
    this.scheduleEnabled = scheduleEnabled;
};
NeatoRobot.prototype.getCharge = function() {
    return this.charge;
};
NeatoRobot.prototype.setCharge = function( charge ) {
    this.charge = charge;
};
NeatoRobot.prototype.getFirmware = function() {
    return this.firmware;
};
NeatoRobot.prototype.setFirmware = function( firmware ) {
    this.firmware = firmware;
};
NeatoRobot.prototype.getLatestFirmware = function() {
    return this.latestFirmware;
};
NeatoRobot.prototype.setLatestFirmware = function( latestFirmware ) {
    this.latestFirmware = latestFirmware;
};
NeatoRobot.prototype.isUpdateAvailable = function( ) {
	return ( this.getFirmware() !== 'undefined' && 
			 this.getFirmware().length > 0 &&
			 this.getLatestFirmware() !== 'undefined' &&
			 this.getLatestFirmware().length > 0 &&
			 this.getFirmware() !== this.getLatestFirmware() 
	);
}
NeatoRobot.prototype.setSchedule = function( schedule ) {
    this.schedule = schedule;
};
NeatoRobot.prototype.getSchedule = function( ) {
    return this.schedule;
};
NeatoRobot.prototype.getNextScheduledEvent = function( ) {
	var nextRun = null;
	$.each( this.schedule, function( index, value ) {	
		var sd = new Date(); 
		// Adjust scheduled date for the time
		var ts = value.startTime.split(":");
		sd.setHours( ts[0] );
		sd.setMinutes( ts[1] );
		// Adjust scheduled date for the weekday
		sd.setDate( sd.getDate() + ( ( 7 + value.day - sd.getDay() ) % 7 ) );
		if ( sd.getTime() < new Date().getTime() ) {
			// Today, but at a time already passed. Add 7 days for next week.
			sd.setDate( sd.getDate() + 7 );
		}
		if ( nextRun == null || nextRun.getTime() > sd.getTime() ) {
			// This scheduled entry is closer
			nextRun = sd;
		}
	});
	// valid date?
	if ( nextRun == null || typeof nextRun.getMonth !== 'function'	) {
		return "Geen";
	}
	var dayStr = dayToStr( nl_NL, nextRun.getDay() );
	if ( nextRun.getDay() == new Date().getDay() ) {
		dayStr = "Vandaag";
	}
	if ( nextRun.getDay() == ( ( new Date().getDay() + 1 ) % 7 ) ) {
		dayStr = "Morgen";
	}
	if ( nextRun.getDay() == ( ( new Date().getDay() + 2 ) % 7 ) ) {
		dayStr = "Overmorgen";
	}
	return dayStr + ' ' + ( nextRun.getHours() < 10 ? '0' : '' ) + nextRun.getHours() + ':' + ( nextRun.getMinutes() < 10 ? '0' : '' ) + nextRun.getMinutes() + 'u';
};
NeatoRobot.prototype.getState = function() {
    return this.state;
};
NeatoRobot.prototype.setState = function( state ) {
    this.state = state;
};
NeatoRobot.prototype.getAction = function() {
    return this.action;
};
NeatoRobot.prototype.setAction = function( action ) {
    this.action = action;
};
NeatoRobot.prototype.setAvailableCommands = function( availableCommands ) {
    this.availableCommands = availableCommands;
};
NeatoRobot.prototype.getAvailableCommands = function( ) {
    return this.availableCommands;
};
NeatoRobot.prototype.isCommandAvailable = function( command ) {
	return ( this.availableCommands[command] !== 'undefined' && 
		     ( this.availableCommands[command] == 1 || this.availableCommands[command] == true || this.availableCommands[command] === "true" ) );
};


// ----------------------- Evohome Location Singleton ------------------------------------------

// Represents an Evohome location
function EHLocation ( locationId ) {
    this.locationId = locationId;
    this.gatewayId = null;
    this.systemType = null;
    this.systemId = null;
    this.mode = null;
    this.isPermanent = null;
    this.zoneIds = [];
}
EHLocation.prototype.getUid = function() {				// To comply with CentralSplashUpdater
    return this.locationId;
};
EHLocation.prototype.getValue = function() {
    return this.getMode();
};
EHLocation.prototype.getHandler = function() {
    return EvohomeUpdateHandler;
};
EHLocation.prototype.getLocationId = function() {
    return this.locationId;
};
EHLocation.prototype.setLocationId = function( locationId ) {
    this.locationId = locationId;
};
EHLocation.prototype.getGatewayId = function() {
    return this.gatewayId;
};
EHLocation.prototype.setGatewayId = function( gatewayId ) {
    this.gatewayId = gatewayId;
};
EHLocation.prototype.getSystemType = function() {
    return this.systemType;
};
EHLocation.prototype.setSystemType = function( systemType ) {
    this.systemType = systemType;
};
EHLocation.prototype.getSystemId = function() {
    return this.systemId;
};
EHLocation.prototype.setSystemId = function( systemId ) {
    this.systemId = systemId;
};
EHLocation.prototype.getMode = function() {
    return this.mode;
};
EHLocation.prototype.setMode = function( mode ) {
    this.mode = mode;
};
EHLocation.prototype.isPermanent = function() {
    return this.isPermanent;
};
EHLocation.prototype.setPermanent = function( permanent ) {
    this.isPermanent = permanent;
};
EHLocation.prototype.getZone = function( zoneId ) {
	if ( !( zoneId in this.zoneIds ) ) {
		// Create new
    	this.zoneIds[ zoneId ] = EHZoneFactory.create( zoneId );
	}
	// Return newly created or existing one
	return this.zoneIds[ zoneId ];
};

/*

    zoneid			evohome zone id. Currently can be any of
        2069237		Badkamer 1
		2306137		Badkamer 2
		2329524		Balzaal
		2069263		Gang
		2329554		Logeerkamer
		2329571		Slaapkamer
		2330410		Vloer
		2297923		Washok
		2069120		Woonkamer
	heatpoint		the temperature to set the device to
	heatpointmode	the duration of the set temperature, can be 
		FollowSchedule		Set the temperature untill the next scheduled switch
							provided nextTime is ignored and derived from the programmed schedule
		PermanentOverride	Set the temperature indefinately
							nextTime is ignored (set to '')
		TemporaryOverride	Hold this temperature until the nextTime value
							If no nextTime is provided a period of 2 hours is assumed
		If omitted, a temporary 2 hours period is assumed (TemporaryOverride).
	nextTime		the time to hold the temperature when status is set to TemporaryOverride.
					If nextTime is in the past, a default 2 hour duration is assumed
		example: 2018-02-15T19:40:27Z

*/
function SplashEHZoneSetpointUpdate( zoneId, heatpoint, heatpointMode = 'FollowSchedule', nextTime = '' ) {
	var jqxhr = $.getJSON( "assets/php/evohome.setzonetemp.php?zoneId=" + zoneId + "&heatpoint=" + heatpoint + "&heatpointMode=" + heatpointMode + "&nextTime" + nextTime, function() {
		console.log( timestamp() + " SplashEHZoneSetpointUpdate(" + zoneId + ", " + heatpoint + ", " + heatpointMode +", " + nextTime + ") - Successful evohome.setzonetemp jqxhr request" );
	})
	.done(function( data ) {
		console.log( timestamp() + " SplashEHZoneSetpointUpdate(" + zoneId + ", " + heatpoint + ", " + heatpointMode +", " + nextTime + ") - Successful evohome.setzonetemp jqxhr response" );
	})
	.fail(function() {
		console.log( timestamp() + " SplashEHZoneSetpointUpdate(" + zoneId + ", " + heatpoint + ", " + heatpointMode +", " + nextTime + ") - Error retrieving device" );
		$.Notification.notify('error','top left', 'Connection error', 'Could not retrieve data for zone (' + zoneId + ')!');
	})
	.always(function() {
		console.log( timestamp() + " SplashEHZoneSetpointUpdate(" + zoneId + ", " + heatpoint + ", " + heatpointMode +", " + nextTime + ") - Done" );
	});
}

function ThrottleSplashEHZoneSetpointUpdate( zoneId, heatpoint, heatpointMode = 'FollowSchedule', nextTime = '' ) {
	console.log( timestamp() + " ThrottleSplashEHZoneSetpointUpdate( " + zoneId + ", " + heatpoint + ", " + heatpointMode + ", " + nextTime + ")");
	const delay = 500;
	const now = (new Date()).getTime();
	if ( !Array.isArray( ThrottleSplashEHZoneSetpointUpdate.zoneIds ) ) {
		ThrottleSplashEHZoneSetpointUpdate.zoneIds = new Array();
	}
	if ( zoneId in ThrottleSplashEHZoneSetpointUpdate.zoneIds && typeof ThrottleSplashEHZoneSetpointUpdate.zoneIds[ zoneId ][ 'time' ] !== 'undefined' && ThrottleSplashEHZoneSetpointUpdate.zoneIds[ zoneId ][ 'time' ] + delay > now ) {
		// Throttle this call. Cancel previous calls and schedule this with new value
		console.log( timestamp() + " ThrottleSplashEHZoneSetpointUpdate( " + zoneId + ", " + heatpoint + ", " + heatpointMode + ", " + nextTime + ") - throttling");
	    clearTimeout( ThrottleSplashEHZoneSetpointUpdate.zoneIds[ zoneId ].timerVar );
		ThrottleSplashEHZoneSetpointUpdate.zoneIds[ zoneId ].timerVar = setTimeout(function() { SplashEHZoneSetpointUpdate( zoneId, heatpoint, heatpointMode, nextTime ); }, delay);
		ThrottleSplashEHZoneSetpointUpdate.zoneIds[ zoneId ].time = now;
	} else {
		// Run this call and register it
		console.log( timestamp() + " ThrottleSplashEHZoneSetpointUpdate( " + zoneId + ", " + heatpoint + ", " + heatpointMode + ", " + nextTime + ") - executing");
		ThrottleSplashEHZoneSetpointUpdate.zoneIds[ zoneId ] = new Array();
		ThrottleSplashEHZoneSetpointUpdate.zoneIds[ zoneId ].time = now;
		SplashEHZoneSetpointUpdate( zoneId, heatpoint, heatpointMode, nextTime );
	}
}
/*
 *   systemId:   SystemId of temperatureControlSystem. E.g.: 123456
 *
 *   mode:       String. Either: "auto", "off", "economy", "away", "dayOff", "custom".
 *
 *   until:      (Optional) Time to apply mode until, can be either:
 *                - Date: date object representing when override should end.
 *                - ISO-8601 date string, in format "yyyy-MM-dd'T'HH:mm:ssXX", e.g.: "2016-04-01T00:00:00Z".
 *                - String: 'permanent'.
 *                - Number: Duration in hours if mode is 'economy', or in days if mode is 'away'/'dayOff'/'custom'.
 *                          Duration will be rounded down to align with Midnight in the local timezone
 *                          (e.g. a duration of 1 day will end at midnight tonight). If 0, mode is permanent.
 *                If 'until' is not specified, a default value is used from the SmartApp settings.

*/
function SplashEHModeUpdate( systemId, mode = 'auto', until = '' ) {
	var jqxhr = $.getJSON( "assets/php/evohome.setmode.php?systemId=" + systemId + "&mode=" + mode + "&until=" + until, function() {
		console.log( timestamp() + " SplashEHModeUpdate(" + systemId + ", " + mode + ", " + until +") - Successful evohome.setzonetemp jqxhr request" );
	})
	.done(function( data ) {
		console.log( timestamp() + " SplashEHModeUpdate(" + systemId + ", " + mode + ", " + until +") - Successful evohome.setzonetemp jqxhr response" );
	})
	.fail(function() {
		console.log( timestamp() + " SplashEHModeUpdate(" + systemId + ", " + mode + ", " + until +") - Error retrieving device" );
		$.Notification.notify('error','top left', 'Connection error', 'Could not retrieve data for system (' + systemId + ')!');
	})
	.always(function() {
		console.log( timestamp() + " SplashEHModeUpdate(" + systemId + ", " + mode + ", " + until +") - Done" );
	});
}

function ThrottleSplashEHModeUpdate( systemId, mode = 'auto', until = '' ) {
	console.log( timestamp() + " ThrottleSplashEHModeUpdate(" + systemId + ", " + mode + ", " + until + ")");
	const delay = 500;
	const now = (new Date()).getTime();
	if ( !Array.isArray( ThrottleSplashEHModeUpdate.systemIds ) ) {
		ThrottleSplashEHModeUpdate.systemIds = new Array();
	}
	if ( systemId in ThrottleSplashEHModeUpdate.systemIds && typeof ThrottleSplashEHModeUpdate.systemIds[ systemId ][ 'time' ] !== 'undefined' && ThrottleSplashEHModeUpdate.systemIds[ systemId ][ 'time' ] + delay > now ) {
		// Throttle this call. Cancel previous calls and schedule this with new value
		console.log( timestamp() + " ThrottleSplashEHModeUpdate(" + systemId + ", " + mode + ", " + until + ") - throttling");
	    clearTimeout( ThrottleSplashEHModeUpdate.systemIds[ systemId ].timerVar );
		ThrottleSplashEHModeUpdate.systemIds[ systemId ].timerVar = setTimeout(function() { SplashEHZoneSetpointUpdate( zoneId, heatpoint, heatpointMode, nextTime ); }, delay);
		ThrottleSplashEHModeUpdate.systemIds[ systemId ].time = now;
	} else {
		// Run this call and register it
		console.log( timestamp() + " ThrottleSplashEHModeUpdate(" + systemId + ", " + mode + ", " + until + ") - executing");
		ThrottleSplashEHModeUpdate.systemIds[ systemId ] = new Array();
		ThrottleSplashEHModeUpdate.systemIds[ systemId ].time = now;
		SplashEHZoneSetpointUpdate( zoneId, heatpoint, heatpointMode, nextTime );
	}
}

// Represents an Evohome device
function EHZone ( zoneId ) {
    this.name = null;
    this.zoneId = zoneId;
    this.temperature = null;
    this.isAvailable = null;
    this.targetTemperature = null;
    this.setpointMode = null;
}

EHZone.prototype.getName = function() {
	return this.name;
};
EHZone.prototype.setName = function( name ) {
    this.name = name;
};
EHZone.prototype.getZoneId = function() {
	return this.zoneId;
};
EHZone.prototype.setZoneId = function( zoneId ) {
    this.zoneId = zoneId;
};
EHZone.prototype.getTemperature = function() {
	return this.temperature;
};
EHZone.prototype.setTemperature = function( temperature ) {
    this.temperature = temperature;
};
EHZone.prototype.isAvailable = function() {
	return this.isAvailable;
};
EHZone.prototype.setAvailable = function( available ) {
    this.isAvailable = available;
};
EHZone.prototype.getTargetTemperature = function() {
	return this.targetTemperature;
};
EHZone.prototype.setTargetTemperature = function( targetTemperature ) {
    this.targetTemperature = targetTemperature;
};
EHZone.prototype.getSetpointMode = function() {
	return this.setpointMode;
};
EHZone.prototype.setSetpointMode = function( setpointMode ) {
    this.setpointMode = setpointMode;
};


function OmnikPortal ( ) {
    this.nowPower = null;
    this.nowPowerUnit = null;
    this.dayPower = null;
    this.dayPowerUnit = null;
    this.monthPower = null;
    this.monthPowerUnit = null;
    this.yearPower = null;
    this.yearPowerUnit = null;
    this.allPower = null;
    this.allPowerUnit = null;
    this.peakPower = null;
    this.peakPowerUnit = null;
}
OmnikPortal.prototype.getUid = function() {
    return "omnikPortal";
};
OmnikPortal.prototype.getValue = function() {
    return this.nowPower;
};
OmnikPortal.prototype.getHandler = function() {
    return OmnikPortalUpdateHandler;
};
OmnikPortal.prototype.getUnit = function() {
    if ( typeof this.nowPowerUnit != 'string' ) { return ''; }
    return this.nowPowerUnit;
};
OmnikPortal.prototype.getEnergyUnit = function() {
    if ( typeof this.dayPowerUnit != 'string' ) { return ''; }
    return this.dayPowerUnit;
};
OmnikPortal.prototype.getEnergy = function() {
    if (parseFloat( this.dayPower ) == 0) { return 0; }
    return this.dayPower;
};
OmnikPortal.prototype.getNowPower = function() {
    return this.nowPower;
};
OmnikPortal.prototype.setNowPower = function( nowPower ) {
    this.nowPower = nowPower;
};
OmnikPortal.prototype.getNowPowerUnit = function() {
    if ( typeof this.nowPowerUnit != 'string' ) { return ''; }
    return this.nowPowerUnit;
};
OmnikPortal.prototype.setNowPowerUnit = function( nowPowerUnit ) {
    this.nowPowerUnit = nowPowerUnit;
};
OmnikPortal.prototype.getDayPower = function() {
    return this.dayPower;
};
OmnikPortal.prototype.setDayPower = function( dayPower ) {
    this.dayPower = dayPower;
};
OmnikPortal.prototype.getDayPowerUnit = function() {
    if ( typeof this.dayPowerUnit != 'string' ) { return ''; }
    return this.dayPowerUnit;
};
OmnikPortal.prototype.setDayPowerUnit = function( dayPowerUnit ) {
    this.dayPowerUnit = dayPowerUnit;
};
OmnikPortal.prototype.getMonthPower = function() {
    return this.monthPower;
};
OmnikPortal.prototype.setMonthPower = function( monthPower ) {
    this.monthPower = monthPower;
};
OmnikPortal.prototype.getMonthPowerUnit = function() {
    if ( typeof this.monthPowerUnit != 'string' ) { return ''; }
    return this.monthPowerUnit;
};
OmnikPortal.prototype.setMonthPowerUnit = function( monthPowerUnit ) {
    this.monthPowerUnit = monthPowerUnit;
};
OmnikPortal.prototype.getYearPower = function() {
    return this.yearPower;
};
OmnikPortal.prototype.setYearPower = function( yearPower ) {
    this.yearPower = yearPower;
};
OmnikPortal.prototype.getYearPowerUnit = function() {
    if ( typeof this.yearPowerUnit != 'string' ) { return ''; }
    return this.yearPowerUnit;
};
OmnikPortal.prototype.setYearPowerUnit = function( yearPowerUnit ) {
    this.yearPowerUnit = yearPowerUnit;
};
OmnikPortal.prototype.getAllPower = function() {
    return this.allPower;
};
OmnikPortal.prototype.setAllPower = function( allPower ) {
    this.allPower = allPower;
};
OmnikPortal.prototype.getAllPowerUnit = function() {
    if ( typeof this.allPowerUnit != 'string' ) { return ''; }
    return this.allPowerUnit;
};
OmnikPortal.prototype.setAllPowerUnit = function( allPowerUnit ) {
    this.allPowerUnit = allPowerUnit;
};
OmnikPortal.prototype.getPeakPower = function() {
    return this.peakPower;
};
OmnikPortal.prototype.setPeakPower = function( peakPower ) {
    this.peakPower = peakPower;
};
OmnikPortal.prototype.getPeakPowerUnit = function() {
    if ( typeof this.peakPowerUnit != 'string' ) { return ''; }
    return this.peakPowerUnit;
};
OmnikPortal.prototype.setPeakPowerUnit = function( peakPowerUnit ) {
    this.peakPowerUnit = peakPowerUnit;
};

// --- 

function HSGraphDataDevice ( ref ) {
    this.ref = ref;
    this.type = null;
    this.data = null;
    this.min = 0;
    this.max = 0;
}
HSGraphDataDevice.prototype.getUid = function() {
    return this.ref;
};
HSGraphDataDevice.prototype.getValue = function() {
    return 0;
};
HSGraphDataDevice.prototype.getHandler = function() {
    return HSGraphDataUpdateHandler;
};
HSGraphDataDevice.prototype.getUnit = function() {
    if ( typeof this.type != 'string' ) { return ''; }
    return this.type;
};
HSGraphDataDevice.prototype.getEnergyUnit = function() {
    if ( typeof this.type != 'string' ) { return ''; }
    return this.type;
};
HSGraphDataDevice.prototype.getEnergy = function() {
    return 0;
};
HSGraphDataDevice.prototype.setType = function( type ) {
    this.type = type;
};
HSGraphDataDevice.prototype.getType = function() {
    return this.type;
};
HSGraphDataDevice.prototype.setData = function( data ) {
    this.data = data;
};
HSGraphDataDevice.prototype.getData = function() {
    return this.data;
};
HSGraphDataDevice.prototype.setMin = function( min ) {
    this.min = min;
};
HSGraphDataDevice.prototype.getMin = function() {
    return this.min;
};
HSGraphDataDevice.prototype.setMax = function( max ) {
    this.max = max;
};
HSGraphDataDevice.prototype.getMax = function() {
    return this.max;
};

// ----------------------- Factory ------------------------------------------

var HSDeviceFactory = {
    refs: [],
    create: function( ref ) {
    	if ( !( ref in this.refs ) ) {
			// Create new
	    	this.refs[ ref ] = new HSDevice( ref );
		}
    	// Return newly created or existing one
    	return this.refs[ ref ];
    },
};

var HSGraphDataDeviceFactory = {
    refs: [],
    create: function( ref ) {
        if ( !( ref in this.refs ) ) {
            // Create new
            this.refs[ ref ] = new HSGraphDataDevice( ref );
        }
        // Return newly created or existing one
        return this.refs[ ref ];
    },
};

var EHLocationFactory = {
    locationIds: [],
    create: function( locationId ) {
    	if ( !( locationId in this.locationIds ) ) {
			// Create new
	    	this.locationIds[ locationId ] = new EHLocation( locationId );
		}
    	// Return newly created or existing one
    	return this.locationIds[ locationId ];
    },
};

var EHZoneFactory = {
    zoneIds: [],
    create: function( zoneId ) {
    	if ( !( zoneId in this.zoneIds ) ) {
			// Create new
	    	this.zoneIds[ zoneId ] = new EHZone( zoneId );
		}
    	// Return newly created or existing one
    	return this.zoneIds[ zoneId ];
    },
};

var NeatoRoboticsFactory = {
    serials: [],
    create: function( serial ) {
    	if ( !( serial in this.serials ) ) {
			// Create new
	    	this.serials[ serial ] = new NeatoRobot( serial );
		}
    	// Return newly created or existing one
    	return this.serials[ serial ];
    },
};

var SoundTouchFactory = {
    ips: [],
    create: function( ip ) {
    	if ( !( ip in this.ips ) ) {
			// Create new
	    	this.ips[ ip ] = new SoundTouch( ip );
		}
    	// Return newly created or existing one
    	return this.ips[ ip ];
    },
};

// just the one
var OmnikPortalFactory = {
    ref: null,
    create: function( ) {
        if ( !( this.ref ) ) {
            // Create new
            this.ref = new OmnikPortal( );
        }
        // Return newly created or existing one
        return this.ref;
    }
};


// Calculate gross energy usage based on total used energy, plus solar power generated, minus solar power returned
// just the one
var GrossNetEnergyCombiDevice = (function () {
    // Instance stores a reference to the Singleton
    var instance;
    var homeSeerNetTotal = null;            // HomeSeer P1 net total use
    var homeSeerNetReturn = null;           // HomeSeer P1 net return
    var homeSeerNetTotalEnergy = null;      // HomeSeer P1 net total use accumulated
    var omnikPortal = null;                 // Omnikportal Gross generation
    var callbacks = null;

    function init() {
        // Singleton
        // Private methods and variables
        homeSeerNetTotal = HSDeviceFactory.create( 267 );           // HomeSeer P1 net total use
        homeSeerNetReturn = HSDeviceFactory.create( 272 );          // HomeSeer P1 net return
        homeSeerNetTotalEnergy = HSDeviceFactory.create( 635 );     // HomeSeer P1 net total use accumulated
        omnikPortal = OmnikPortalFactory.create();                  // Omnikportal Gross generation
        callbacks = new Array();

        return {
            // Public methods and variables
            getUid: function( ) {
                // unique id
                return 'gnecd';
            },
            getUnit: function( ) {
                // Unit
                return 'W';
            },
            getValue: function( ) { 
                //
                var netTotalVal = ( homeSeerNetTotal && typeof homeSeerNetTotal.getValue === 'function' && jQuery.isNumeric( homeSeerNetTotal.getValue() ) ? parseFloat( homeSeerNetTotal.getValue() ) : 0 );
                var netTotalUnit = ( homeSeerNetTotal && typeof homeSeerNetTotal.getUnit === 'function' ? homeSeerNetTotal.getUnit() : '' );
                var netReturnVal = ( homeSeerNetReturn && typeof homeSeerNetReturn.getValue === 'function' && jQuery.isNumeric( homeSeerNetReturn.getValue() ) ? parseFloat( homeSeerNetReturn.getValue() ) : 0 );
                var netReturnUnit = ( homeSeerNetReturn && typeof homeSeerNetReturn.getUnit === 'function' ? homeSeerNetReturn.getUnit() : '' );
                var omnikPortalVal = ( omnikPortal && typeof omnikPortal.getValue === 'function' && jQuery.isNumeric( omnikPortal.getValue() ) ? parseFloat( omnikPortal.getValue() ) : 0 );
                var omnikPortalUnit = ( omnikPortal && typeof omnikPortal.getUnit === 'function' ? omnikPortal.getUnit() : '' );
                // Calculate - net used energy
                var value = 0; 
                switch( netTotalUnit ) {
                    case 'W':
                        value += netTotalVal; 
                        break;
                    case 'kW':
                        value += ( netTotalVal * 1000 ); 
                        break;
                    default:
                        value += netTotalVal; 
                }
                // Calculate - plus generated energy
                switch( omnikPortalUnit ) {
                    case 'W':
                        value += omnikPortalVal; 
                        break;
                    case 'kW':
                        value += ( omnikPortalVal * 1000 ); 
                        break;
                    default:
                        value += omnikPortalVal; 
                }
                // Calculate - minus returned energy
                switch( netReturnUnit ) {
                    case 'W':
                        value -= ( netReturnVal * 1000 ); 
                        break;
                    case 'kW':
                        value -= ( netReturnVal * 1000 ); 
                        break;
                    default:
                        value -= netReturnVal; 
                }
                return value;
            },
            getEnergy: function( ) {
                var netTotalEnergy = ( homeSeerNetTotalEnergy && typeof homeSeerNetTotalEnergy.getValue === 'function' && jQuery.isNumeric( homeSeerNetTotalEnergy.getValue() ) ? parseFloat( homeSeerNetTotalEnergy.getValue() ) : 0 );
                var netTotalEnergyUnit = ( homeSeerNetTotalEnergy && typeof homeSeerNetTotalEnergy.getUnit === 'function' ? homeSeerNetTotalEnergy.getUnit() : '' );
                var omnikPortalEnergyVal = ( omnikPortal && typeof omnikPortal.getEnergy === 'function' && jQuery.isNumeric( omnikPortal.getEnergy() ) ? parseFloat( omnikPortal.getEnergy() ) : 0 );
                var omnikPortalEnergyUnit = ( omnikPortal && typeof omnikPortal.getEnergyUnit === 'function' ? omnikPortal.getEnergyUnit() : '' );
                // Calculate - net used energy
                var value = 0; 
                switch( netTotalEnergyUnit ) {
                    case 'Wh':
                        value += netTotalEnergy; 
                        break;
                    case 'kWh':
                        value += ( netTotalEnergy * 1000 ); 
                        break;
                    default:
                        value += netTotalEnergy; 
                }
                // Calculate - plus generated energy
                switch( omnikPortalEnergyUnit ) {
                    case 'Wh':
                        value += omnikPortalEnergyVal; 
                        break;
                    case 'kWh':
                        value += ( omnikPortalEnergyVal * 1000 ); 
                        break;
                    default:
                        value += omnikPortalEnergyVal; 
                }
                value = value / 1000;
                if ( value == 0 || Math.round(value *100) == 0 ) { return 0; }
                if ( value < 1 && value > 0 ) { return (Math.round(value *100) /100).toFixed(3); }
                if ( value >= 1 && value < 100 ) {
                    if ( (Math.round(value * 10) /10).toFixed(1) != Math.round(value) ) return (Math.round(value * 10) /10).toFixed(1);
                    return value;
                }
                if ( value >= 100 ) {
                    return Math.round(value); 
                }
                return value;
            },
            getEnergyUnit: function( ) {
                return 'kWh';
            },
            getHomeSeerNetTotal: function( ) {
                return homeSeerNetTotal;
            },
            getHomeSeerNetReturn: function( ) {
                return homeSeerNetReturn;
            },
            getHomeSeerNetTotalEnergy: function( ) {
                return homeSeerNetTotalEnergy;
            },
            getOmnikPortal: function( ) {
                return omnikPortal;
            },
            register: function( callback ) {
                // Add handler
                callbacks.push( callback );
            },
            notify: function ( ) {
                $.each( callbacks, function( index, callback ) {
                    // Make sure the callback is a function
                    if (typeof callback === "function") {
                        // Call it, since we have confirmed it is callable
                        callback( );
                    }
                });
            } 
        };
 
    };
 
    return {
        // Get the Singleton instance if one exists
        // or create one if it doesn't
        getInstance: function () {
            if ( !instance ) {
                // Create new
                instance = init();
                // Register
                CentralSplashUpdater.register( instance.getHomeSeerNetTotal().getUid(), instance.getHomeSeerNetTotal().getHandler(), function() { instance.notify() } );
                CentralSplashUpdater.register( instance.getHomeSeerNetReturn().getUid(), instance.getHomeSeerNetReturn().getHandler(), function() { instance.notify() } );
                CentralSplashUpdater.register( instance.getOmnikPortal().getUid(), instance.getOmnikPortal().getHandler(), function() { instance.notify() } );
                CentralSplashUpdater.register( instance.getHomeSeerNetTotalEnergy().getUid(), instance.getHomeSeerNetTotalEnergy().getHandler(), function() { instance.notify() } );
            }
            return instance;
        },
       homeSeerNetTotal: homeSeerNetTotal
 };
 
})();



// ----------------------- Homeseer Energy Device Object ------------------------------------------

function SplashCirclifulEnergyDevice( name ) {
    // Element tot attach it to
    this.name = name;
    this.subtitle = '';
    this.bindingElement = null;
    // Default width class. Works with col-lg-4, col-lg-6 and col-12
    this.widthClass = 'col-lg-3';   // col-lg-3 col-md-6
    this.fgColor = "#3bafda";
    this.bgColor = "#505A66";
    this.fillColor = "#36404a";

    this.source = null;
    this.sourceEnergy = null;
    this.scale = 2000;
    this.registerSplashUpdater = true;
}
SplashCirclifulEnergyDevice.prototype.getName = function( ) {
    return this.name;
}
SplashCirclifulEnergyDevice.prototype.setSubtitle = function( subtitle ) {
    this.subtitle = subtitle;
}
SplashCirclifulEnergyDevice.prototype.getSubtitle = function( ) {
    return this.subtitle;
}
SplashCirclifulEnergyDevice.prototype.setBindingElement = function( bindingElement ) {
    this.bindingElement = bindingElement;
}
SplashCirclifulEnergyDevice.prototype.getBindingElement = function( ) {
    return this.bindingElement;
}
SplashCirclifulEnergyDevice.prototype.setSource = function( source ) {
    this.source = source;
}
SplashCirclifulEnergyDevice.prototype.getSource = function( ) {
    return this.source;
}
SplashCirclifulEnergyDevice.prototype.setWidthClass = function( widthClass ) {
    this.widthClass = widthClass;
}
SplashCirclifulEnergyDevice.prototype.getWidthClass = function( ) {
    return this.widthClass;
}
SplashCirclifulEnergyDevice.prototype.getFgColor = function( ) {
    return this.fgColor;
}
SplashCirclifulEnergyDevice.prototype.setFgColor = function( fgColor ) {
    this.fgColor = fgColor;
}
SplashCirclifulEnergyDevice.prototype.getBgColor = function( ) {
    return this.bgColor;
}
SplashCirclifulEnergyDevice.prototype.setBgColor = function( bgColor ) {
    this.bgColor = bgColor;
}
SplashCirclifulEnergyDevice.prototype.getFillColor = function( ) {
    return this.fillColor;
}
SplashCirclifulEnergyDevice.prototype.setFillColor = function( fillColor ) {
    this.fillColor = fillColor;
}
SplashCirclifulEnergyDevice.prototype.getScale = function( ) {
    return this.scale;
}
SplashCirclifulEnergyDevice.prototype.setScale = function( scale ) {
    this.scale = scale;
}
SplashCirclifulEnergyDevice.prototype.setRegisterSplashUpdater = function( registerSplashUpdater ) {
    this.registerSplashUpdater = registerSplashUpdater;
}
SplashCirclifulEnergyDevice.prototype.getRegisterSplashUpdater = function( ) {
    return this.registerSplashUpdater;
}
SplashCirclifulEnergyDevice.prototype.setSourceEnergy = function( sourceEnergy ) {
    this.sourceEnergy = sourceEnergy;
}
SplashCirclifulEnergyDevice.prototype.getSourceEnergy = function( ) {
    return this.sourceEnergy;
}

SplashCirclifulEnergyDevice.prototype.draw = function( ) {
    console.log( timestamp() + " SplashCirclifulEnergyDevice.draw()");
    var source = this.getSource();
    var uid = source.getUid();
    var sourceEnergy  = this.getSourceEnergy() ;

    // Does the element exist? No: draw, Yes: update
    if ( $('#sced_' + uid).length ) {
        console.log( timestamp() + " SplashCirclifulEnergyDevice.draw() - Update the element");

        var value = source.getValue();
        var unit = source.getUnit();
        var scale = this.getScale();
        if ( value < 1000 && unit == 'kW' ) {
            // convert to W
            value = value * 1000;
            unit = 'W';
            scale = scale * 1000;
        }
        if (value > scale) {
            scale = value * 1.1;
            if ( scale < 1 && scale > 0 ) { scale = (Math.round(scale *100) /100).toFixed(3); }
            if ( scale >= 1 && scale < 100 ) { 
                if ( Math.round(scale) != scale ) {
                    scale = (Math.round(scale *10) /10).toFixed(1);
                } // else scale = scale
            }
        }
        $('#sced_' + uid + '_scale_min').html(0+unit);
        $('#sced_' + uid + '_scale_max').html(scale+unit);
          
        $('#sced_'+uid+'_energy').toggleClass('invisible', ( sourceEnergy == null ));         
        $('#sced_'+uid+'_energytitle').toggleClass('invisible', ( sourceEnergy == null ));         
        if ( sourceEnergy != null ) {
            $('#sced_'+uid+'_energy').html(sourceEnergy.getEnergy()+sourceEnergy.getEnergyUnit());
            // Update the tooltip
            $('#sced_'+uid+'_energy').attr('data-original-title', '€ ' + (Math.round( (0.22 * sourceEnergy.getEnergy()) *100) /100).toFixed(2));
        }

        if ( $('#sced_'+uid+'_circliful').attr('data-percent') != Math.round((value/scale)*100) ||
             $('#sced_'+uid+'_circliful').attr('data-text') != value+' '+unit ) {
            // Change
            $('#sced_' + uid + '_circliful').empty().removeData().attr('data-percent', Math.round((value/scale)*100)).attr('data-text', value+' '+unit).attr('data-fgcolor', this.getFgColor()).attr('data-fill', this.getFillColor()).attr('data-bgcolor', this.getBgColor()).circliful();
        }
    } else {
        // Element dows not exist, draw it
        console.log( timestamp() + " SplashCirclifulEnergyDevice.draw() - Drawing new element");

        var elStr = `<div id="sced_TOKEN_ID" class="TOKEN_WIDTHCLASS" style="height: 220px; overflow: hidden; margin-bottom: 20px;">
                <div class="card-box">
                    <h6 id="sced_TOKEN_ID_scale_min" class="" style="position: absolute; top: 197px; right: 50%; margin-right: 73px; text-align: right;">...W</h6>
                    <h6 id="sced_TOKEN_ID_scale_max" class="" style="position: absolute; top: 197px; left: 50%; margin-left: 73px; text-align: left;">...W</h6>

                    <h5 id="sced_TOKEN_ID_energy" class="invisible" data-toggle="tooltip" data-placement="bottom" title="€ 0,00" style="position: absolute; top: 20px; right: 20px; text-align: right; color: TOKEN_FGCOLOR;">...W</h5>
                    <h6 id="sced_TOKEN_ID_energytitle" class="invisible" style="position: absolute; top: 35px; right: 20px; text-align: right;">Vandaag</h6>
                    <h4 class="m-t-0 header-title"><b>TOKEN_NAME</b></h4>
                    <p class="text-muted m-b-30 font-13">TOKEN_SUBTITLE</p>
                    <div class="slrdb_activity_wrapper">
                        <div class="row text-center">
                            <div class="col-sm-6 col-lg-3">
                                <div id="sced_TOKEN_ID_circliful" class="circliful-chart" data-dimension="200" data-text="0" data-info="TOKEN_NAME" data-width="30" data-fontsize="24" data-percent="0" data-fgcolor="TOKEN_FGCOLOR" data-bgcolor="TOKEN_BGCOLOR" data-type="half" data-fill="TOKEN_FILLCOLOR"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>`;

        elStr = elStr.replace( /TOKEN_ID/g, uid );
        elStr = elStr.replace( /TOKEN_NAME/g, this.getName() );
        elStr = elStr.replace( /TOKEN_SUBTITLE/g, this.getSubtitle() );
        elStr = elStr.replace( /TOKEN_WIDTHCLASS/g, this.getWidthClass() );
        elStr = elStr.replace( /TOKEN_FGCOLOR/g, this.getFgColor() );
        elStr = elStr.replace( /TOKEN_BGCOLOR/g, this.getBgColor() );
        elStr = elStr.replace( /TOKEN_FILLCOLOR/g, this.getFillColor() );
               
        $( this.getBindingElement() ).append( elStr );
        $('#sced_'+uid+'_energy').tooltip(); 

        $('#sced_'+uid+'_circliful').circliful();

        var obj = this;
        if ( this.getRegisterSplashUpdater() ) {
            CentralSplashUpdater.register( source.getUid(), source.getHandler(), function() { obj.draw() } );
            if ( sourceEnergy != null ) {
                CentralSplashUpdater.register( sourceEnergy.getUid(), sourceEnergy.getHandler(), function() { obj.draw() } );
            }
        }
    }
}






// ----------------------- Homeseer Energy Device Object ------------------------------------------

function SplashEnergyDevice( name ) {
    // Element tot attach it to
    this.name = name;
    this.bindingElement = null;
    // Default width class. Works with col-lg-4, col-lg-6 and col-12
    this.widthClass = 'col-lg-3';   // col-lg-3 col-md-6

    this.power = null;
    this.energy = null;
    this.maxPower = null;

}
SplashEnergyDevice.prototype.getName = function( ) {
    return this.name;
}
SplashEnergyDevice.prototype.setBindingElement = function( bindingElement ) {
    this.bindingElement = bindingElement;
}
SplashEnergyDevice.prototype.getBindingElement = function( ) {
    return this.bindingElement;
}
SplashEnergyDevice.prototype.setWidthClass = function( widthClass ) {
    this.widthClass = widthClass;
}
SplashEnergyDevice.prototype.getWidthClass = function( ) {
    return this.widthClass;
}
SplashEnergyDevice.prototype.setPower = function( ref ) {
    this.power = HSDeviceFactory.create( ref );
};
SplashEnergyDevice.prototype.getPower = function( ref ) {
    return this.power;
};
SplashEnergyDevice.prototype.setEnergy = function( ref ) {
    this.energy = HSDeviceFactory.create( ref );
};
SplashEnergyDevice.prototype.getEnergy = function( ) {
    return this.energy;
};
SplashEnergyDevice.prototype.setMaxPower = function( ref ) {
    this.maxPower = HSDeviceFactory.create( ref );
};
SplashEnergyDevice.prototype.getMaxPower = function( ) {
    return this.maxPower;
};

SplashEnergyDevice.prototype.draw = function( ) {
    console.log( timestamp() + " SplashEnergyDevice.draw()");
    var power = this.getPower();
    var energy = this.getEnergy();
    var maxPower = this.getMaxPower();
    var uniqueString = (power?power.getRef():'')+(energy?energy.getRef():'')+(maxPower?maxPower.getRef():'');
    
    // Does the element exist? No: draw, Yes: update
    if ( $('#send_' + uniqueString).length ) {
        console.log( timestamp() + " SplashEnergyDevice.draw() - Update the element");

        $('#send_' + uniqueString + ' .energy_col_1').html( $('#send_' + uniqueString).index() +1 ); // row number
        $('#send_' + uniqueString + ' .energy_col_2').html( power.getLocation2() );    // Locatie
        $('#send_' + uniqueString + ' .energy_col_3').html( power.getLocation() );     // Locatie
        $('#send_' + uniqueString + ' .energy_col_4').html( (this.getName()?this.getName():power.getName()) );         // Device

        $('#send_' + uniqueString + ' .energy_col_5').html( (power?power.getValue():'-') );       // Waarde
        $('#send_' + uniqueString + ' .energy_col_5').attr( 'title', (power?'ref: '+power.getRef():'-') );
        $('#send_' + uniqueString + ' .energy_col_6').html( (maxPower?maxPower.getValue():'-') ); // Waarde
        $('#send_' + uniqueString + ' .energy_col_6').attr( 'title', (maxPower?'ref: '+maxPower.getRef():'-') );
        $('#send_' + uniqueString + ' .energy_col_7').html( (energy?energy.getValue():'-') );     // Waarde
        $('#send_' + uniqueString + ' .energy_col_7').attr( 'title', (energy?'ref: '+energy.getRef():'-') );

        $('#send_' + uniqueString + ' .energy_col_8').html( power.getStatus() );       // Eenheid

    } else {
        // Element dows not exist, draw it
        console.log( timestamp() + " SplashEnergyDevice.draw() - Drawing new element");

        var elStr = `<tr id="send_TOKEN_ID" class="settings_row">
                <td class="energy_col_1" scope="row">..</th>
                <td class="energy_col_2">..</td>
                <td class="energy_col_3 text-center">..</td>
                <td class="energy_col_4 text-left">..</td>
                <td class="energy_col_5 text-center">..</td>
                <td class="energy_col_6"></th>
                <td class="energy_col_7"></th>
                <td class="energy_col_8"></th>
                <td class="energy_col_9"></th>
                <td class="energy_col_10"><i class="mdi mdi-battery-charging-40"> </i></th>
            </tr>`;

        elStr = elStr.replace( /TOKEN_ID/g, uniqueString );
                
        $( this.getBindingElement() + ' tbody' ).append( elStr );

        var obj = this;
        if (power) { CentralSplashUpdater.register( power.getRef(), HSUpdateHandler, function() { obj.draw() } ); }
        if (energy) { CentralSplashUpdater.register( energy.getRef(), HSUpdateHandler, function() { obj.draw() } ); } 
        if (maxPower) { CentralSplashUpdater.register( maxPower.getRef(), HSUpdateHandler, function() { obj.draw() } ); } 
    }
}



// ----------------------- Homeseer Energy Graph Object ------------------------------------------

function SplashEnergyGraph( name ) {
    // Element tot attach it to
    this.name = name;
    this.uniqueId = makeId( 5 );
    this.bindingElement = null;
    // Default width class. Works with col-lg-4, col-lg-6 and col-12
    this.widthClass = 'col-lg-3';   // col-lg-3 col-md-6

    this.refList = [];
    this.flotGraph = null;

}
SplashEnergyGraph.prototype.getName = function( ) {
    return this.name;
}
SplashEnergyGraph.prototype.setBindingElement = function( bindingElement ) {
    this.bindingElement = bindingElement;
}
SplashEnergyGraph.prototype.getBindingElement = function( ) {
    return this.bindingElement;
}
SplashEnergyGraph.prototype.setWidthClass = function( widthClass ) {
    this.widthClass = widthClass;
}
SplashEnergyGraph.prototype.getWidthClass = function( ) {
    return this.widthClass;
}
SplashEnergyGraph.prototype.addElement = function( el ) {
    this.refList.push( { ref: el.ref, label: el.label, color: el.color, obj: HSGraphDataDeviceFactory.create( el.ref ) } );
};

var flotGraphs = [];

SplashEnergyGraph.prototype.draw = function( ) {
    console.log( timestamp() + " SplashEnergyDevice.draw()");
    
    // Does the element exist? No: draw, Yes: update
    if ( $('#seg_' + this.uniqueId).length ) {
        console.log( timestamp() + " SplashEnergyGraph.draw() - Update the element");

        // Build the dataset
        var newYMin = null, newYMax = null;
        var flotDataset = []
        $.each( this.refList, function( index, value ) {
            flotDataset.push( {
                label: value.label, 
                data: value.obj.getData() 
            });
            if ( newYMin == null || value.obj.getMin() < newYMin ) { newYMin = value.obj.getMin(); }
            if ( newYMax == null || value.obj.getMax() > newYMax ) { newYMax = value.obj.getMax(); }
        });
        this.flotGraph.setData( flotDataset );
 
        var opts = this.flotGraph.getOptions();
        opts.yaxes[0].min = newYMin;
        opts.yaxes[0].max = newYMax;

        opts.yaxes[0].panRange = [newYMin, newYMax];


        $('#seg_' + this.uniqueId + '_waiting').toggleClass( 'invisible', true );

                

        this.flotGraph.setupGrid();
        this.flotGraph.draw();

    } else {
        // Element dows not exist, draw it
        console.log( timestamp() + " SplashEnergyGraph.draw() - Drawing new element");

        var elStr = `<div id="seg_TOKEN_ID" class="TOKEN_WIDTHCLASS">
            <div class="portlet"><!-- /primary heading -->
                <div class="portlet-heading">
                    <h3 class="portlet-title text-dark">TOKEN_NAME</h3>
                    <div class="clearfix"></div>
                    <div class="btn-group" style="position: absolute; top: 20px; right: 30px;">
                        <button type="button" id="seg_TOKEN_ID_week" class="btn btn-outline-light waves-effect waves-light" style="width: 70px;" onclick="flotGraphs[ 'seg_TOKEN_ID' ].getOptions().xaxes[0].min = (new Date(new Date().getFullYear(), new Date().getMonth(), new Date().getDate() - 7)).getTime(); flotGraphs[ 'seg_TOKEN_ID' ].getOptions().xaxes[0].tickSize = [ 1, 'day' ]; flotGraphs[ 'seg_TOKEN_ID' ].setupGrid(); flotGraphs[ 'seg_TOKEN_ID' ].draw();"> Week </button>
                        <button type="button" id="seg_TOKEN_ID_today" class="btn btn-outline-light waves-effect waves-light" style="width: 70px;" onclick="flotGraphs[ 'seg_TOKEN_ID' ].getOptions().xaxes[0].min = (new Date(new Date().getFullYear(), new Date().getMonth(), new Date().getDate() - 1)).getTime(); flotGraphs[ 'seg_TOKEN_ID' ].getOptions().xaxes[0].tickSize = [ 4, 'hour' ]; flotGraphs[ 'seg_TOKEN_ID' ].setupGrid(); flotGraphs[ 'seg_TOKEN_ID' ].draw();"> Today </button>
                   </div>
                    <div class="btn-group" style="position: absolute; top: 55px; left: 67px;">
                        <button type="button" id="seg_TOKEN_ID_yaxeszoomout" class="btn btn-outline-secondary btn-sm waves-effect waves-light" style="width: 38px;" onclick="flotGraphs[ 'seg_TOKEN_ID' ].getOptions().yaxes[0].max = flotGraphs[ 'seg_TOKEN_ID' ].getOptions().yaxes[0].max / 2; flotGraphs[ 'seg_TOKEN_ID' ].setupGrid(); flotGraphs[ 'seg_TOKEN_ID' ].draw();"> <i class="fa fa-search-plus"></i> </button>
                        <button type="button" id="seg_TOKEN_ID_yaxeszoomin" class="btn btn-outline-secondary btn-sm waves-effect waves-light" style="width: 38px;" onclick="flotGraphs[ 'seg_TOKEN_ID' ].getOptions().yaxes[0].max = flotGraphs[ 'seg_TOKEN_ID' ].getOptions().yaxes[0].max * 2; flotGraphs[ 'seg_TOKEN_ID' ].setupGrid(); flotGraphs[ 'seg_TOKEN_ID' ].draw();"> <i class="fa fa-search-minus"></i> </button>
                   </div>
                </div>
                <div id="portlet TOKEN_ID" class="panel-collapse collapse show">
                    <div class="portlet-body">
                        <div id="seg_TOKEN_ID_flotgraph" style="height: 320px;" class="flot-chart"></div>
                        <div id="seg_TOKEN_ID_waiting" style="position: absolute; top: 50%; left: 50%; font-size: 30px;" class="flot-chart"> <i class="fa fa-refresh fa-spin fa-7x"></i> </div>
                    </div>
                </div>
            </div>
        </div>`;

        elStr = elStr.replace( /TOKEN_ID/g, this.uniqueId );
        elStr = elStr.replace( /TOKEN_NAME/g, this.getName() );
        elStr = elStr.replace( /TOKEN_WIDTHCLASS/g, this.getWidthClass() );
                
        $( this.getBindingElement() ).append( elStr );

        var flotDataset = [];
        var flotColors = [];
        $.each( this.refList, function( index, value ) {
            flotDataset.push( {
                label: value.label, 
                data: null 
            });
            flotColors.push( value.color );
        });

        this.flotGraph = $.plot($("#seg_"+this.uniqueId+"_flotgraph"), flotDataset, {
            legend: {
                position: 'ne',
                backgroundColor: '#eeeeff',
                backgroundOpacity: 0.5,
                show: true
            },
            series: {
//                stack: true,        // Stacked lines
                lines: {
                    show: true,
                    fill: true,
                    fillColor: { colors: [{ opacity: 0.7 }, { opacity: 0.1}] },
                },
                points: {
                    show: false
                },
                grow : {
                    active : true
                } //disable auto grow
            },
            colors: flotColors,
            grid : {
                show : true,
                aboveData : false,
                color : '#36404a',
                labelMargin : 15,
                axisMargin : 0,
                borderWidth : 0,
                borderColor : null,
                minBorderMargin : 5,
                clickable : true,
                hoverable : true,
                autoHighlight : false,
                mouseActiveRadius : 20
            },
            tooltip : true, //activate tooltip
            tooltipOpts : {
                content: function(label, xval, yval, flotItem) {
                    var d = new Date(xval);
                    if ( yval > 1000 ) {
                        return '<span style="color: ' + flotItem.series.color + '; font-weight: bold;"> ' + label +'</span><br>' + (yval / 1000) + 'kWh<br><i class="fa fa-calendar"></i> ' + d.getDate() + " " + monthToStr( nl_NL, d.getMonth() ) + " " + d.getFullYear() + ' <i class="fa fa-clock-o"></i> ' + (d.getHours()<10?'0':'') + d.getHours() + ":" + (d.getMinutes()<10?'0':'') + d.getMinutes() + "u";
                    }
                    return '<span style="color: ' + flotItem.series.color + '; font-weight: bold;"> ' + label +'</span><br>' + yval + 'Wh<br><i class="fa fa-calendar"></i> ' + d.getDate() + " " + monthToStr( nl_NL, d.getMonth() ) + " " + d.getFullYear() + ' <i class="fa fa-clock-o"></i> ' + (d.getHours()<10?'0':'') + d.getHours() + ":" + (d.getMinutes()<10?'0':'') + d.getMinutes() + "u";
                },
                shifts : {
                    x : -60,
                    y : -80
                }
            },
            zoom: {
                interactive: true,
                trigger: "dblclick" // or "click" for single click
            },
            pan: {
                interactive: true,
                cursor: "move"      // CSS mouse cursor value used when dragging, e.g. "pointer"
                },
            yaxis: {
                min: 0, 
                max: 1000,
                font : {
                    color : '#98a6ad'
                },
                panRange: [0, 1000]
            },
            xaxis: { 
                show : true,
                font : {
                    color : '#98a6ad'
                },
//                tickDecimals: 0,
                timezone: 'browser',
                minTickSize: [1, "day"],
//                twelveHourClock: false,
                mode: "time",
                min: (new Date(new Date().getFullYear(), new Date().getMonth(), new Date().getDate() - 7)).getTime(),
                max: (new Date()).getTime(),
                zoomRange: [(new Date(new Date().getFullYear(), new Date().getMonth(), new Date().getDate() - 7)).getTime(), (new Date()).getTime()],
                panRange: [(new Date(new Date().getFullYear(), new Date().getMonth(), new Date().getDate() - 7)).getTime(), (new Date()).getTime()]
            }
        });

        flotGraphs[ 'seg_' + this.uniqueId ] = this.flotGraph;

        $('#seg_'+this.uniqueId+'_flotgraph').bind("plotpan", function (event, plot) {
        });

        $('#seg_'+this.uniqueId+'_flotgraph').bind("plotzoom", function (event, plot) {
            var axes = plot.getAxes();
            if ( ( axes.xaxis.max - axes.xaxis.min ) > (1.5 * 24 * 60 * 60 * 1000) ) {
                // switch to day xaxis
                axes.xaxis.options.tickSize = [1, "day"];
            } else {
                // switch to 4-hour xaxis
                axes.xaxis.options.tickSize = [4, "hours"];
            }
            plot.setupGrid();
            plot.draw();

        });

        var obj = this;
        $.each( this.refList, function( key, value ) {
            CentralSplashUpdater.register( value.ref, HSGraphDataUpdateHandler, function() { obj.draw() } );
        });
    }
}

// ----------------------- Bose SoundTouch Device Object ------------------------------------------
// Represents a Splash Bose SoundTouch device
function SplashSoundTouch ( ip ) {
    this.soundTouch = SoundTouchFactory.create( ip );
    // Element tot attach it to
    this.bindingElement = null;
	// Default width class. Works with col-lg-4 and col-lg-6
    this.widthClass = 'col-lg-6';
}

SplashSoundTouch.prototype.getSoundTouch = function( ) {
	return this.soundTouch;
}
SplashSoundTouch.prototype.setBindingElement = function( bindingElement ) {
	this.bindingElement = bindingElement;
}
SplashSoundTouch.prototype.getBindingElement = function( ) {
	return this.bindingElement;
}
SplashSoundTouch.prototype.setWidthClass = function( widthClass ) {
	this.widthClass = widthClass;
}
SplashSoundTouch.prototype.getWidthClass = function( ) {
	return this.widthClass;
}


SplashSoundTouch.prototype.draw = function( ) {
	console.log( timestamp() + " SplashSoundTouch.draw()");
	var soundTouch = this.getSoundTouch();
	var ip = soundTouch.getIP();
	var ipId = ip.replace(/\./g, "");

	// Remove the spinner
	$('#bstd_' + ipId + '_activity_refresh_button').addClass('btn-outline-secondary');
	$('#bstd_' + ipId + '_activity_refresh_button').removeClass('btn-secondary'); 
	$('#bstd_' + ipId + '_activity_refresh').removeClass('fa-spin');
	
	// Does the element exist? No: draw, Yes: update
	if ( $('div#bstd_' + ipId).length ) {
		console.log( timestamp() + " SplashSoundTouch.draw() - Update the element");

		$('#bstd_'+ipId+'_name').html( soundTouch.getName() );

		switch ( soundTouch.getNowPlayingStatusString() ) {
			case "Spotify":
				$('div#bstd_'+ipId+'_nowPlaying_controls').slideDown();
				$('div#bstd_'+ipId+'_nowPlaying_spotify').slideDown();
				$('div#bstd_'+ipId+'_nowPlaying_internetradio').slideUp();
				break;
			case "Internet Radio":
				$('div#bstd_'+ipId+'_nowPlaying_controls').slideDown();
				$('div#bstd_'+ipId+'_nowPlaying_spotify').slideUp();
				$('div#bstd_'+ipId+'_nowPlaying_internetradio').slideDown();
				break;
			case "Notification":
				$('div#bstd_'+ipId+'_nowPlaying_controls').slideDown();
				$('div#bstd_'+ipId+'_nowPlaying_spotify').slideUp();
				$('div#bstd_'+ipId+'_nowPlaying_internetradio').slideUp();
				$('div#bstd_'+ipId+'_nowPlaying_notification').slideDown();
				break;
			case "Standby":
			default:
				$('div#bstd_'+ipId+'_nowPlaying_controls').slideUp();
				$('div#bstd_'+ipId+'_nowPlaying_spotify').slideUp();
				$('div#bstd_'+ipId+'_nowPlaying_internetradio').slideUp();
		}

		// STANDBY SPOTIFY INTERNET_RADIO
		$('#bstd_'+ipId+'_activity_text').html( soundTouch.getNowPlayingStatusHtml() );
		$('#bstd_'+ipId+'_volume').html( "Volume: " + soundTouch.getVolume() );

		$.each( soundTouch.getPresets(), function( index, preset ) {
			// Remove the preset
			$('button#bstd_'+ipId+'_' + preset.id + 'img').remove();
			$('button#bstd_'+ipId+'_' + preset.id + 'div').remove();
			$('button#bstd_'+ipId+'_' + preset.id).text("");		
			if ( preset.containerArt !== 'undefined' && typeof preset.containerArt == 'string' && preset.containerArt.length > 10 ) {
				// Use art
				$('button#bstd_'+ipId+'_' + preset.id).append( '<img class="" style="max-width: 40px; max-height: 40px;" src="' + preset.containerArt + '">' );
			} else {
				// Use text
				$('button#bstd_'+ipId+'_' + preset.id).append( '<div style="font-size: xx-small; max-width: 50px; overflow: hidden; text-overflow:ellipsis;">' + preset.itemName + '</div>' );
			}

		});

		// Fill the Now Playing section
		$('button#bstd_'+ipId+'_repeat').toggleClass("btn-outline-secondary", !soundTouch.isRepeatEnabled() );
		$('button#bstd_'+ipId+'_repeat').toggleClass("btn-outline-light", soundTouch.isRepeatEnabled() );
		$('button#bstd_'+ipId+'_random').toggleClass("btn-outline-secondary", !soundTouch.isShuffleEnabled() );
		$('button#bstd_'+ipId+'_random').toggleClass("btn-outline-light", soundTouch.isShuffleEnabled() );

		$('button#bstd_'+ipId+'_previous').toggleClass("disabled", !soundTouch.isSkipPreviousEnabled() );
		$('button#bstd_'+ipId+'_previous').prop("disabled", !soundTouch.isSkipPreviousEnabled() );
		
		$('button#bstd_'+ipId+'_play').toggleClass("disabled", soundTouch.isPlaying() );
		$('button#bstd_'+ipId+'_play').prop("disabled", soundTouch.isPlaying() );
		
		$('button#bstd_'+ipId+'_pause').toggleClass("disabled", !soundTouch.isPlaying() );
		$('button#bstd_'+ipId+'_pause').prop("disabled", !soundTouch.isPlaying() );

		$('button#bstd_'+ipId+'_stop').toggleClass("disabled", !soundTouch.isStopped() );
		$('button#bstd_'+ipId+'_stop').prop("disabled", !soundTouch.isStopped() );

		$('button#bstd_'+ipId+'_next').toggleClass("disabled", !soundTouch.isSkipEnabled() );
		$('button#bstd_'+ipId+'_next').prop("disabled", !soundTouch.isSkipEnabled() );

		$('#bstd_'+ipId+'_nowPlaying_s_art').attr('src', soundTouch.getArt());
		$('#bstd_'+ipId+'_nowPlaying_ir_art').attr('src', soundTouch.getArt());
		
		$('#bstd_'+ipId+'_nowPlaying_station').html( soundTouch.getStationName() );
		
		if ( soundTouch.isPlaylist() ) {
			$('#bstd_'+ipId+'_nowPlaying_playlist').slideDown();
		} else {
			$('#bstd_'+ipId+'_nowPlaying_playlist').slideUp();
		}			
		$('#bstd_'+ipId+'_nowPlaying_playlist').html( soundTouch.getPlaylist() );
		
		$('#bstd_'+ipId+'_nowPlaying_description').html( soundTouch.getDescription() );
		$('#bstd_'+ipId+'_nowPlaying_location').html( soundTouch.getStationLocation() );
		$('#bstd_'+ipId+'_nowPlaying_track').html( soundTouch.getTrack() + ' - ' + soundTouch.getArtist() );

		// Check if the Notification Server is available -> mark red and disable
		$('#bstd_'+ipId+'_showAudioFiles').toggleClass("btn-outline-secondary", NotificationServer.isAvailable() );
		$('#bstd_'+ipId+'_showAudioFiles').toggleClass("btn-danger", !NotificationServer.isAvailable() );
		$('#bstd_'+ipId+'_showAudioFiles').prop("disabled", !NotificationServer.isAvailable() );
		if ( !NotificationServer.isAvailable() ) {
			// slide up, make red, and disable
			$('#bstd_'+ipId+'_nowPlaying_notification').slideUp();
		}

	} else {
		// Element dows not exist, draw it
		console.log( timestamp() + " SplashSoundTouch.draw() - Drawing new element");

		var elStr = `<div class="col-lg-6" id="bstd_TOKEN_IPNODOTS">
			<div class="card-box bstd-card-box">
				<div class="bstd-top">
					<div class="bstd-logo-device">
						<img src="assets/images/BOSE-SoundTouch-20-III-wit-small.png">
					</div>
					<div class="bstd-logo-brand">
						<img src="assets/images/Bose_logo.png">
					</div>
					<div class="bstd-notification">
						<button type="button" id="bstd_TOKEN_IPNODOTS_showAudioFiles" class="btn btn-outline-secondary btn-sm waves-effect waves-light m-l-5 m-r-5" onclick="$('#bstd_TOKEN_IPNODOTS_nowPlaying_notification').slideToggle();"> <i class="fa fa-bullhorn m-l-5 m-r-5"> </i> </button>
					</div>
					<div class="bstd-activity-box">
						<h3 id="bstd_TOKEN_IPNODOTS_activity_text" class="m-t-2 m-b-5 p-b-2 text-light">...</h3>
						<h6 id="bstd_TOKEN_IPNODOTS_volume" class="text-muted m-t-2">...</h6>
					</div>
					<div class="bstd-refresh-box">
						<button type="button" id="bstd_TOKEN_IPNODOTS_activity_refresh_button" class="btn btn-outline-secondary waves-effect waves-light m-l-5 m-r-5" onclick="$('#bstd_TOKEN_IPNODOTS_activity_refresh_button').addClass('btn-secondary');$('#bstd_TOKEN_IPNODOTS_activity_refresh_button').removeClass('btn-outline-secondary'); $('#bstd_TOKEN_IPNODOTS_activity_refresh').addClass('fa-spin'); CentralSplashUpdater.update( BoseUpdateHandler.uidt, 'TOKEN_IPWITHDOTS' );"> <i id="bstd_TOKEN_IPNODOTS_activity_refresh" class="fa fa-refresh m-l-5 m-r-5"> </i></button>
					</div>
					<div class="bstd-refresh-box">
						<h5 id="bstd_TOKEN_IPNODOTS_name" class="m-t-2 m-b-5 p-b-2 text-secondary" style="padding-left: 130px; padding-top: 25px; width: 300px;">...</h5>
					</div>
				</div>
				<div>
					<div class="bstd_activity_wrapper">
					    <div class="btn-group">
							<div class="btn-group-vertical">
								<button type="button" id="bstd_TOKEN_IPNODOTS_powerOff" class="btn btn-outline-light waves-effect waves-light" style="width: 50px;" onclick="ThrottleSplashSoundTouchUpdate( 'TOKEN_IPWITHDOTS', 'POWER' );"> <i class="fa fa-power-off"> </i> </button>
								<button type="button" id="bstd_TOKEN_IPNODOTS_BTaux" class="btn btn-outline-light waves-effect waves-light" style="width: 50px;" onclick="ThrottleSplashSoundTouchUpdate( 'TOKEN_IPWITHDOTS', 'AUX' );"><span style="font-weight: lighter; font-size: xx-small;"><i class="fa fa-bluetooth-b"> | AUX</i></span></button>
							</div>
							<div class="btn-group-vertical">
							    <div class="btn-group">
									<button type="button" id="bstd_TOKEN_IPNODOTS_1" class="btn btn-outline-light btn-lg waves-effect waves-light" style="width: 70px;" onclick="ThrottleSplashSoundTouchUpdate( 'TOKEN_IPWITHDOTS', 'PRESET_1' );"> 1 </button>
									<button type="button" id="bstd_TOKEN_IPNODOTS_2" class="btn btn-outline-light btn-lg waves-effect waves-light" style="width: 70px;" onclick="ThrottleSplashSoundTouchUpdate( 'TOKEN_IPWITHDOTS', 'PRESET_2' );"> 2 </button>
									<button type="button" id="bstd_TOKEN_IPNODOTS_3" class="btn btn-outline-light btn-lg waves-effect waves-light" style="width: 70px;" onclick="ThrottleSplashSoundTouchUpdate( 'TOKEN_IPWITHDOTS', 'PRESET_3' );"> 3 </button>
								</div>
								<div class="btn-group">
									<button type="button" id="bstd_TOKEN_IPNODOTS_4" class="btn btn-outline-light btn-lg waves-effect waves-light" style="width: 70px;" onclick="ThrottleSplashSoundTouchUpdate( 'TOKEN_IPWITHDOTS', 'PRESET_4' );"> 4 </button>
									<button type="button" id="bstd_TOKEN_IPNODOTS_5" class="btn btn-outline-light btn-lg waves-effect waves-light" style="width: 70px;" onclick="ThrottleSplashSoundTouchUpdate( 'TOKEN_IPWITHDOTS', 'PRESET_5' );"> 5 </button>
									<button type="button" id="bstd_TOKEN_IPNODOTS_6" class="btn btn-outline-light btn-lg waves-effect waves-light" style="width: 70px;" onclick="ThrottleSplashSoundTouchUpdate( 'TOKEN_IPWITHDOTS', 'PRESET_6' );"> 6 </button>
								</div>
							</div>
							<div class="btn-group-vertical">
								<button type="button" id="bstd_TOKEN_IPNODOTS_volumeUp" class="btn btn-outline-light waves-effect waves-light" style="width: 50px;" onclick="ThrottleSplashSoundTouchUpdate( 'TOKEN_IPWITHDOTS', 'VOLUME_UP' );"> <i class="fa fa-volume-off"><span style="font-weight: bold;"> + </span></i> </button>
								<button type="button" id="bstd_TOKEN_IPNODOTS_volumeDown" class="btn btn-outline-light waves-effect waves-light" style="width: 50px;" onclick="ThrottleSplashSoundTouchUpdate( 'TOKEN_IPWITHDOTS', 'VOLUME_DOWN' );"> <i class="fa fa-volume-off"><span style="font-weight: bold;"> - </span></i> </button>
							</div>
		                </div>
		            </div>
		        </div>
				<div id="bstd_TOKEN_IPNODOTS_nowPlaying_controls">
					<div class="nrr_schedule_wrapper" style="width: 100%; padding-top: 10px; padding-bottom: 20px; text-align: center;">
						<div style=" padding: 10px;">
							<button type="button" id="bstd_TOKEN_IPNODOTS_repeat" class="btn btn-outline-secondary waves-effect waves-light" style="width: 50px;" onclick="ThrottleSplashSoundTouchUpdate( 'TOKEN_IPWITHDOTS', 'TOGGLE_REPEAT' );"> <i class="fa fa-repeat"></i> </button>
							<button type="button" id="bstd_TOKEN_IPNODOTS_random" class="btn btn-outline-secondary waves-effect waves-light" style="width: 50px;" onclick="ThrottleSplashSoundTouchUpdate( 'TOKEN_IPWITHDOTS', 'TOGGLE_SHUFFLE' );"> <i class="fa fa-random"></i> </button>
							<div class="btn-group">
								<button type="button" id="bstd_TOKEN_IPNODOTS_previous" class="btn btn-outline-secondary waves-effect waves-light disabled" style="width: 50px;" onclick="ThrottleSplashSoundTouchUpdate( 'TOKEN_IPWITHDOTS', 'PREV_TRACK' );" disabled> <i class="fa fa-step-backward"></i> </button>
								<button type="button" id="bstd_TOKEN_IPNODOTS_play" class="btn btn-outline-secondary waves-effect waves-light disabled" style="width: 50px;" onclick="ThrottleSplashSoundTouchUpdate( 'TOKEN_IPWITHDOTS', 'PLAY' );" disabled> <i class="fa fa-play"></i> </button>
								<button type="button" id="bstd_TOKEN_IPNODOTS_pause" class="btn btn-outline-secondary waves-effect waves-light disabled" style="width: 50px;" onclick="ThrottleSplashSoundTouchUpdate( 'TOKEN_IPWITHDOTS', 'PAUSE' );" disabled> <i class="fa fa-pause"></i> </button>
								<button type="button" id="bstd_TOKEN_IPNODOTS_stop" class="btn btn-outline-secondary waves-effect waves-light disabled" style="width: 50px;" onclick="ThrottleSplashSoundTouchUpdate( 'TOKEN_IPWITHDOTS', 'POWER' );" disabled> <i class="fa fa-stop"></i> </button>
								<button type="button" id="bstd_TOKEN_IPNODOTS_next" class="btn btn-outline-secondary waves-effect waves-light disabled" style="width: 50px;" onclick="ThrottleSplashSoundTouchUpdate( 'TOKEN_IPWITHDOTS', 'NEXT_TRACK' );" disabled> <i class="fa fa-step-forward"></i> </button>
							</div>
						</div>
					</div>
				</div>
				<div id="bstd_TOKEN_IPNODOTS_nowPlaying_internetradio">
					<div class="nrr_schedule_wrapper" style="width: 100%; padding-top: 10px; padding-bottom: 20px; text-align: center;">
						<div style="width: 100%; padding-top: 20px;">
							<img id="bstd_TOKEN_IPNODOTS_nowPlaying_ir_art" style="max-width: 60px; max-height: 60px;" src="/assets/images/Bose_logo.png">
							<h5 id="bstd_TOKEN_IPNODOTS_nowPlaying_station" class="m-t-2 m-b-5 p-b-2 text-warning" style="padding-top: 20px;"></h5>
							<h6 id="bstd_TOKEN_IPNODOTS_nowPlaying_description" style="padding-top: 20px;"></h6>
							<h6 id="bstd_TOKEN_IPNODOTS_nowPlaying_location"></h6>
						</div>
					</div>
				</div>
				<div id="bstd_TOKEN_IPNODOTS_nowPlaying_spotify">
					<div class="nrr_schedule_wrapper" style="width: 100%; padding-top: 10px; padding-bottom: 20px; text-align: center;">
						<div style="width: 100%; padding-top: 20px;">
							<img id="bstd_TOKEN_IPNODOTS_nowPlaying_s_art" style="max-width: 60px; max-height: 60px;" src="/assets/images/Bose_logo.png">
							<h5 id="bstd_TOKEN_IPNODOTS_nowPlaying_playlist" class="m-t-2 m-b-5 p-b-2 text-muted" style="padding-top: 20px;"></h5>
							<h5 id="bstd_TOKEN_IPNODOTS_nowPlaying_track" class="m-t-2 m-b-5 p-b-2 text-muted" style="padding-top: 20px;"></h5>
							<h5 class="fa fa-spotify fa-2x" style="color: #1db954; padding-top: 10px;"> </h5>
						</div>
					</div>
				</div>
				<div id="bstd_TOKEN_IPNODOTS_nowPlaying_notification">
					<div class="nrr_schedule_wrapper" style="width: 100%; padding-top: 0px; padding-bottom: 20px; text-align: center;">
						<div style="width: 100%; padding-top: 20px;">
							<h5 class="fa fa-bullhorn fa-2x text-warning" style="padding-top: 10px;"> </h5>
						</div>
						<div style="padding: 10px;">
		                    <div class="btn-group" style="width: 300px;">
			                    <button type="button" class="btn btn-outline-warning dropdown-toggle waves-effect waves-light" style="width: 400px;" data-toggle="dropdown" aria-expanded="false">Notifications<span class="caret"></span></button>
			                    <div class="dropdown-menu scrollable-menu" id="bstd_TOKEN_IPNODOTS_audioFilesDropdown">
			                    </div>
		                    </div>
						</div>
					</div>
				</div>
		
			</div>
		</div>`;

		elStr = elStr.replace( /TOKEN_IPNODOTS/g, ipId );
		elStr = elStr.replace( /TOKEN_IPWITHDOTS/g, ip );
		$( this.getBindingElement() ).append( elStr );

		$.getScript("assets/php/audio.list.php", function() {
			$( audioFiles ).each(function( index, audioFileUrl ) {
				var audioFileName = decodeURIComponent( audioFileUrl ).split('/').pop();	// Remove URL
				audioFileName = audioFileName.split('.')[0];	// Remove extension
				audioFileName = audioFileName.replace(/_/g, " ");	// Cleanup underscores
				audioFileName = audioFileName.replace(/-/g, " ");	// Cleanup dashes
				audioFileName = audioFileName.toUpperCaseEachWord();	// CamelCase
				$('#bstd_'+ipId+'_audioFilesDropdown').append('<a class="dropdown-item btn-outline-warning" href="#" onclick="SplashPlaySoundTouchNotification( \'' + ip + '\', \'' + audioFileUrl + '\' );"><i class="fa fa-bullhorn"></i> ' + audioFileName + '</a>');
			});
		});
		$('#bstd_'+ipId+'_nowPlaying_controls').slideUp();		
		$('#bstd_'+ipId+'_nowPlaying_internetradio').slideUp();
		$('#bstd_'+ipId+'_nowPlaying_spotify').slideUp();
		$('#bstd_'+ipId+'_nowPlaying_notification').slideUp();
		// Register for updates. Bind the callback to this object
		var obj = this;
		CentralSplashUpdater.register( ip, BoseUpdateHandler, function() { obj.draw() } );
		
		// Register for Notification Server status updates (availablity)
		NotificationServer.register( function() { obj.draw() } );
	}
}

/* 
Cannot play a notification if one is already playing or paused. First switch to another media or switch off
*/
function SplashPlaySoundTouchNotification( ip, audioFileUrl ) {
	console.log( timestamp() + " SplashPlaySoundTouchNotification()");
    var soundTouch = SoundTouchFactory.create( ip );
	if ( soundTouch.getNowPlayingStatusString() == 'Notification' ) {
		$.Notification.notify('warning','top left', 'Notification', "Cannot play a new Notification when another Notification is already playing. Switch to another media type or switch the SoundTouch OFF before playing another Notification.");	
		return;
	}
	ThrottleSplashSoundTouchUpdate( ip, 'SPEAKER', 30, audioFileUrl, 'Splash' );
}
// ----------------------- Neato Robot Device Object ------------------------------------------
// Represents a Splash Neato Robot device
function SplashNeatoRobot ( serial ) {
    this.robot = NeatoRoboticsFactory.create( serial );
    // Element tot attach it to
    this.bindingElement = null;
	// Default width class. Works with col-lg-4 and col-lg-6
    this.widthClass = 'col-lg-6';
}

SplashNeatoRobot.prototype.getRobot = function( ) {
	return this.robot;
}
SplashNeatoRobot.prototype.setBindingElement = function( bindingElement ) {
	this.bindingElement = bindingElement;
}
SplashNeatoRobot.prototype.getBindingElement = function( ) {
	return this.bindingElement;
}
SplashNeatoRobot.prototype.setWidthClass = function( widthClass ) {
	this.widthClass = widthClass;
}
SplashNeatoRobot.prototype.getWidthClass = function( ) {
	return this.widthClass;
}


SplashNeatoRobot.prototype.draw = function( ) {
	console.log( timestamp() + " SplashNeatoRobot.draw()");
	var robot = this.getRobot();
	var serial = robot.getSerial();
	// Remove the spinner
	$('#nrr_' + serial + '_activity_refresh_button').addClass('btn-outline-secondary');
	$('#nrr_' + serial + '_activity_refresh_button').removeClass('btn-secondary'); 
	$('#nrr_' + serial + '_activity_refresh').removeClass('fa-spin');
	// Does the element exist? No: draw, Yes: update
	if ( $('div#nrr_' + serial).length ) {
		console.log( timestamp() + " SplashNeatoRobot.draw() - Update the element");

		// Toggle button visibility, make green start button if enabled
		$('button#nrr_' + serial + '_startCleaning').toggleClass("disabled", !(robot.isCommandAvailable( 'start' ) || robot.isCommandAvailable( 'resume' )) );
		$('button#nrr_' + serial + '_startCleaning').prop('disabled', !(robot.isCommandAvailable( 'start' ) || robot.isCommandAvailable( 'resume' )) );
		$('#nrr_' + serial + '_startCleaning').toggleClass('btn-outline-success', robot.isCommandAvailable( 'start' ) || robot.isCommandAvailable( 'resume' ) );
		$('#nrr_' + serial + '_startCleaning').toggleClass('btn-outline-mute', !(robot.isCommandAvailable( 'start' ) || robot.isCommandAvailable( 'resume' )));
		
		$('button#nrr_' + serial + '_pauseResumeCleaning').toggleClass("disabled", !robot.isCommandAvailable( 'pause' ) );
		$('button#nrr_' + serial + '_pauseResumeCleaning').prop('disabled', !robot.isCommandAvailable( 'pause' ) );
		$('button#nrr_' + serial + '_stopCleaning').toggleClass("disabled", !robot.isCommandAvailable( 'stop' ) );
		$('button#nrr_' + serial + '_stopCleaning').prop('disabled', !robot.isCommandAvailable( 'stop' ));
		$('button#nrr_' + serial + '_sendToBase').toggleClass("d-none", !robot.isCommandAvailable( 'goToBase' ) );

		// Wirl if active
		$('#nrr_' + serial + '_startCleaning i').toggleClass( 'fa-spin', robot.getState() == 2 );

		$('#nrr_' + serial + '_charge_text').html( robot.getCharge() + '%' );

		$('h3#nrr_' + serial + '_activity_text').toggleClass("text-success", false);
		$('h3#nrr_' + serial + '_activity_text').toggleClass("text-light", true);
		$('h3#nrr_' + serial + '_activity_text').toggleClass("text-error", false);
		if ( robot.isCharging() ) {
			// On dock, and charging
			$('h3#nrr_' + serial + '_activity_text').html("Charging");
		} else if ( robot.isDocked() ) {
			// Docked
			$('h3#nrr_' + serial + '_activity_text').html("Docked");
		} else if ( robot.isError() ) {
			$('h3#nrr_' + serial + '_activity_text').toggleClass("text-success", false);
			$('h3#nrr_' + serial + '_activity_text').toggleClass("text-light", false);
			$('h3#nrr_' + serial + '_activity_text').toggleClass("text-error", true);
			switch( robot.getErrorString() ) {
				case 'ui_error_brush_stuck':
					$('h3#nrr_' + serial + '_activity_text').html("Borstel vastgelopen");
					break;
				case 'ui_error_vacuum_stuck':
					$('h3#nrr_' + serial + '_activity_text').html("Vastgelopen");
					break;
				case 'ui_error_dust_bin_full':
					$('h3#nrr_' + serial + '_activity_text').html("Afvalbak vol");
					break;
				case 'ui_error_navigation_pathproblems_returninghome':
					$('h3#nrr_' + serial + '_activity_text').html("Navigatieprobleem");
					break;
				default:
					$('h3#nrr_' + serial + '_activity_text').html("Probleempje...");
					break;
			}
		} else {
			// Not docked and not in error, check the state, running maybe?
			//  State 1 (action 0) - Stopped
			//  State 2 (action 1) - Started
			//  State 3 (action 1) - Paused
			switch ( robot.getState() ) {
				case 1:	// Stopped
					$('h3#nrr_' + serial + '_activity_text').html("Stopped");
					break;
				case 2:	// Started
					$('h3#nrr_' + serial + '_activity_text').html("Active!");
					$('h3#nrr_' + serial + '_activity_text').toggleClass("text-success", true);
					$('h3#nrr_' + serial + '_activity_text').toggleClass("text-light", false);
					$('h3#nrr_' + serial + '_activity_text').toggleClass("text-error", false);
					break;
				case 3:	// Paused
					$('h3#nrr_' + serial + '_activity_text').html("Paused");
					break;
				default:
					$('h3#nrr_' + serial + '_activity_text').html("...");
			}
		}
		$('input#nrr_' + serial + '_schedule_myonoffswitch').prop('checked', robot.isScheduleEnabled());
		// Firmware
		$('span#nrr_' + serial + '_available-firmware').html( robot.getLatestFirmware() );
		$('span#nrr_' + serial + '_current-firmware').html( robot.getFirmware() );			
		if ( robot.isUpdateAvailable() ) {
			// Firmware update available
			$('#nrr_' + serial + '_showFirmware').removeClass('invisible');
		}

		// Remove the schedule
		$( "div#nrr_" + serial + "_schedule h6" ).remove( );
		// Show the schedule button
		if ( robot.getSchedule().length > 0 ) {
			$('#nrr_' + serial + '_showSchedule').removeClass('invisible');
		} else {
			$('#nrr_' + serial + '_showSchedule').addClass('invisible');
		}
		// Update the schedule
		$.each( robot.getSchedule(), function( index, sEvent ) {
			$( 'div#nrr_' + serial + '_schedule' ).append( '<h6 class="m-t-2 m-b-5 p-b-2 text-muted" style="padding-left: 20px;">' + dayToStr( nl_NL, sEvent.day ) + ' ' +  sEvent.startTime + 'u ' + neatoModeToStr( nl_NL, sEvent.mode ) + '</h6>' );
		});
		// Update next scheduled			
		$( 'span#nrr_' + serial + '_next_scheduled_run' ).html( robot.getNextScheduledEvent() );

	} else {
		// Element dows not exist, draw it
		console.log( timestamp() + " SplashNeatoRobot.draw() - Drawing new element");

		var elStr = `<div class="col-lg-6" id="nrr_TOKEN_NEATOSERIAL">
			<div class="card-box nr-card-box">
				<div class="nr-top">
					<div class="nr-logo-device">
						<img src="assets/images/NeatoBotvacConnected.png">
					</div>
					<div class="nr-logo-brand">
						<img src="assets/images/neato-logo.png">
					</div>
					<div class="nr-show-schedule">
						<button type="button" id="nrr_TOKEN_NEATOSERIAL_showSchedule" class="btn btn-outline-secondary btn-sm waves-effect waves-light invisible" onclick="$('#nrr_TOKEN_NEATOSERIAL_show-schedule').slideToggle();"> <i class="fa fa-calendar-check-o"> </i> </button>
					</div>
					<div class="nr-firmware-update">
						<button type="button" id="nrr_TOKEN_NEATOSERIAL_showFirmware" class="btn btn-outline-warning btn-sm waves-effect waves-light invisible" onclick="$('#nrr_TOKEN_NEATOSERIAL_firmware').slideToggle();"> <i class="fa fa-warning"> </i> </button>
					</div>
					<div class="nr-activity-box">
						<h3 id="nrr_TOKEN_NEATOSERIAL_activity_text" class="m-t-2 m-b-5 p-b-2 text-light">...</h3>
						<h6 id="nrr_TOKEN_NEATOSERIAL_charge_text" class="text-muted m-t-2">...</h6>
					</div>
					<div class="nr-refresh-box">
						<button type="button" id="nrr_TOKEN_NEATOSERIAL_activity_refresh_button" class="nrr_TOKEN_NEATOSERIAL_color btn btn-outline-secondary waves-effect waves-light m-l-5 m-r-5" onclick="$('#nrr_TOKEN_NEATOSERIAL_activity_refresh_button').addClass('btn-secondary');$('#nrr_TOKEN_NEATOSERIAL_activity_refresh_button').removeClass('btn-outline-secondary'); $('#nrr_TOKEN_NEATOSERIAL_activity_refresh').addClass('fa-spin'); CentralSplashUpdater.update( NRUpdateHandler.uidt, 'TOKEN_NEATOSERIAL' );"> <i id="nrr_TOKEN_NEATOSERIAL_activity_refresh" class="fa fa-refresh m-l-5 m-r-5"> </i></button>
					</div>
				</div>
				<div>
					<div class="nrr_activity_wrapper">
						<button type="button" id="nrr_TOKEN_NEATOSERIAL_startCleaning" class="slhd_activity btn btn-outline-light w-lg waves-effect waves-light disabled" onclick="ThrottleSplashNRRobotUpdate( 'TOKEN_NEATOSERIAL', 'startCleaning' );" disabled> <i class="fa fa-eercast fa-2x"> </i> </button>
						<button type="button" id="nrr_TOKEN_NEATOSERIAL_pauseResumeCleaning" class="slhd_activity btn btn-outline-light w-lg waves-effect waves-light disabled" onclick="ThrottleSplashNRRobotUpdate( 'TOKEN_NEATOSERIAL', 'pauseCleaning' );" disabled> <i class="fa fa-pause fa-2x"> </i> </button>
						<button type="button" id="nrr_TOKEN_NEATOSERIAL_stopCleaning" class="slhd_activity btn btn-outline-light w-lg waves-effect waves-light disabled" onclick="ThrottleSplashNRRobotUpdate( 'TOKEN_NEATOSERIAL', 'stopCleaning' );" disabled> <i class="fa fa-stop fa-2x"> </i> </button>
						<button type="button" id="nrr_TOKEN_NEATOSERIAL_sendToBase" class="slhd_activity btn btn-outline-light w-lg waves-effect waves-dark d-none" onclick="ThrottleSplashNRRobotUpdate( 'TOKEN_NEATOSERIAL', 'sendToBase' );"> <i class="fa fa-arrow-right"> </i><i class="fa fa-home fa-2x"> </i> </button>
					</div>
				</div>
				<div id="nrr_TOKEN_NEATOSERIAL_show-schedule">
					<div class="nrr_schedule_wrapper" style="padding-top: 10px; padding-bottom: 20px;">
						<div style="width: 280px; padding-top: 20px;">
							<h5 class="m-t-2 m-b-5 p-b-2 text-muted" style="padding-left: 20px;">Next scheduled run: <span id="nrr_TOKEN_NEATOSERIAL_next_scheduled_run" class="text-light">...</span></h5>
						</div>
						<div style="display: flex; width: 280px; padding-top: 20px;">
							<h5 class="m-t-2 m-b-5 p-b-2 text-light" style="width: 200px; padding-right: 20px; text-align: right; line-height: 30px; vertical-align: middle;">Enable schedule:</h5>
							<div style="flex: 1;">
								<div class="onoffswitch">
								    <input type="checkbox" name="onoffswitch" class="onoffswitch-checkbox" id="nrr_TOKEN_NEATOSERIAL_schedule_myonoffswitch">
								    <label class="onoffswitch-label" for="nrr_TOKEN_NEATOSERIAL_schedule_myonoffswitch">
								        <span class="onoffswitch-inner"></span>
								        <span class="onoffswitch-switch"></span>
								    </label>
								</div>
							</div>
						</div>
						<div id="nrr_TOKEN_NEATOSERIAL_schedule" style="width: 280px; padding-top: 20px;">
							<h4 class="m-t-2 m-b-5 p-b-2 text-light" style="padding-left: 20px;">Schedule</h4>
						</div>
					</div>
				</div>
				
				<div id="nrr_TOKEN_NEATOSERIAL_firmware">
					<div class="nrr_schedule_wrapper" style="width: 100%; padding-top: 10px; padding-bottom: 20px; text-align: center;">
						<div style="width: 100%; padding-top: 20px;">
							<h5 class="m-t-2 m-b-5 p-b-2 text-warning" style="">Firmware <span id="nrr_TOKEN_NEATOSERIAL_available-firmware">...</span> update available.</h5>
						</div>
						<div style="width: 100%;">
							<h6 class="m-t-2 m-b-5 p-b-2 text-light" style="">Current firmware <span id="nrr_TOKEN_NEATOSERIAL_current-firmware">...</span></h6>
						</div>
					</div>
				</div>
			</div>
		</div>`;

		elStr = elStr.replace( /TOKEN_NEATOSERIAL/g, serial );
		$( this.getBindingElement() ).append( elStr );

		$('#nrr_'+serial+'_show-schedule').slideUp();
		$('#nrr_'+serial+'_firmware').slideUp();
		var obj = this;
		$('#nrr_' + serial + '_schedule_myonoffswitch').change( obj.switchScheduleOnOff );
		// Register for updates. Bind the callback to this object
		CentralSplashUpdater.register( serial, NRUpdateHandler, function() { obj.draw() } );
	}
}

SplashNeatoRobot.prototype.switchScheduleOnOff = function( serial ) {
	console.log( timestamp() + " SplashNeatoRobot.switchScheduleOnOff()");
	var robot = NeatoRoboticsFactory.create( serial );
	ThrottleSplashNRRobotUpdate( serial, ( robot.isScheduleEnabled( ) ? 'disableSchedule' : 'enableSchedule' ) );
	robot.setScheduleEnabled( !robot.isScheduleEnabled( ) );
}



// ----------------------- Harmony Device Object ------------------------------------------
// Represents a Splash Harmony device
//  [ 797, 'Woonkamer',	'SplashHarmonyDevice',	null ], // Harmony - Activity (1: PowerOff, 2: TV kijken, 3: Radio, 4: Flubbertje muziek, 5: Flubbertje, 6: iTV met Marantz, 7: Gramofon)
//	[ 798, 'Woonkamer',	'SplashHarmonyDevice',	null ], // Harmony - TV ontvanger (1: PowerToggle, 2: 0, 3: 1, 4: 2, 5: 3, 6: 4, 7: 5, 8: 6, 9: 7, 10: 8, 11: 9, 12: Mute, 13: Channel Down, 14: ChannelUp, 15: DirectionDown, 16: DirectionLeft, 17: DirectionRight, 18: DirectionUp, 19: Select, 20: Stop, 21: Rewind, 22: Pause, 23: FastForward, 24: Record, 25: SlowForward, 26: Menu, 27: Teletext, 28: Green, 29: Red, 30: Blue, 31: Yellow, 32: Guide, 33: Info, 34: Cancel, 36: Radio, 39: TV)
//	[ 799, 'Woonkamer',	'SplashHarmonyDevice',	null ], // Harmony - Receiver (1: PowerOff, 2: PowerOn, 16: Mute, 17: VolumeDown, 18: VolumeUp)
//	[ 800, 'Woonkamer',	'SplashHarmonyDevice',	null ], // Harmony - ChromeCast Flubbertje
//	[ 801, 'Woonkamer',	'SplashHarmonyDevice',	null ], // Harmony - TV (1: PowerOff, 2: PowerOn, 14: Mute, 15: VolumeDown, 16: VolumeUp, 41: AmbiLight, 42: AmbiMode)
//
// We can get the status from the activity, but the devices can only be sent to. Therefore only the ref is required.
// The chromecast cannot be controlled, hence the ref is not required
//
function SplashHarmonyDevice ( ref ) {
    this.hsdev = HSDeviceFactory.create( ref );
    this.hsdevTVReceiver = 0;
    this.hsdevReceiver = 0;
    this.hsdevTV = 0;
    // Element tot attach it to
    this.bindingElement = null;
}

SplashHarmonyDevice.prototype.getHSDev = function( ) {
	return this.hsdev;
}
SplashHarmonyDevice.prototype.setBindingElement = function( bindingElement ) {
	this.bindingElement = bindingElement;
}
SplashHarmonyDevice.prototype.getBindingElement = function( ) {
	return this.bindingElement;
}
SplashHarmonyDevice.prototype.setTVReceiverRef = function( tvReceiverRef ) {
	this.hsdevTVReceiver = tvReceiverRef;
}
SplashHarmonyDevice.prototype.getTVReceiverRef = function( ) {
	return this.hsdevTVReceiver;
}
SplashHarmonyDevice.prototype.setReceiverRef = function( receiverRef ) {
	this.hsdevReceiver = receiverRef;
}
SplashHarmonyDevice.prototype.getReceiverRef = function( ) {
	return this.hsdevReceiver;
}
SplashHarmonyDevice.prototype.setTVRef = function( tvRef ) {
	this.hsdevTV = tvRef;
}
SplashHarmonyDevice.prototype.getTVRef = function( ) {
	return this.hsdevTV;
}

SplashHarmonyDevice.prototype.draw = function( ) {
	console.log( timestamp() + " SplashHarmonyDevice.draw()");
	var hsDev = this.getHSDev();
	var ref = hsDev.getRef();
	// Remove the spinner
	$('#slhd_'+ref+'_activity_refresh_button').addClass('btn-outline-secondary');
	$('#slhd_'+ref+'_activity_refresh_button').removeClass('btn-secondary'); 
	$('#slhd_'+ref+'_activity_refresh').removeClass('fa-spin');
	// Does the element exist? No: draw, Yes: update
	if ( $('div#slhd_' + ref).length ) {
		console.log( timestamp() + " SplashHarmonyDevice.draw() - Update the element");

		// Harmony - Activity (1: PowerOff, 2: TV kijken, 3: Radio, 4: Flubbertje muziek, 5: Flubbertje, 6: iTV met Marantz, 7: Gramofon)
		$('button#slhd_'+ref+'_tv').removeClass('btn-warning');			$('button#slhd_'+ref+'_tv').addClass('btn-outline-warning');
		$('button#slhd_'+ref+'_spotify').removeClass('btn-spotify');	$('button#slhd_'+ref+'_spotify').addClass('btn-outline-spotify');
		$('button#slhd_'+ref+'_radio').removeClass('btn-info');			$('button#slhd_'+ref+'_radio').addClass('btn-outline-info');
		$('button#slhd_'+ref+'_off').removeClass('btn-light');			$('button#slhd_'+ref+'_off').addClass('btn-outline-light');
		switch ( hsDev.getValue() ) {
			case 7:		// Gramofon
				$('div#slhd_'+ref+'_tvpresets').slideUp();
				$('div#slhd_'+ref+'_radiopresets').slideUp();
				$('div#slhd_'+ref+'_colorbuttons').slideUp();
				$('div#slhd_'+ref+'_videocontrols').slideUp();
				$('div#slhd_'+ref+'_updownleftrightcontrols').slideUp();
				$('div#slhd_'+ref+'_volumecontrols').slideDown();
				$('div#slhd_'+ref+'_exitguidecontrols').slideUp();
				$('div#slhd_'+ref+'_mutemenucontrols').slideUp();
				$('div#slhd_'+ref+'_mutecontrol').slideUp();
				$('button#slhd_'+ref+'_spotify').addClass('btn-spotify');
				$('button#slhd_'+ref+'_spotify').removeClass('btn-outline-spotify');
				$('h3#slhd_'+ref+'_activity_text').html('Gramofon');
				break;
			case 6:		// iTV met Marantz
				$('div#slhd_'+ref+'_tvpresets').slideUp();
				$('div#slhd_'+ref+'_radiopresets').slideUp();
				$('div#slhd_'+ref+'_colorbuttons').slideUp();
				$('div#slhd_'+ref+'_videocontrols').slideDown();
				$('div#slhd_'+ref+'_updownleftrightcontrols').slideDown();
				$('div#slhd_'+ref+'_volumecontrols').slideDown();
				$('div#slhd_'+ref+'_exitguidecontrols').slideDown();
				$('div#slhd_'+ref+'_mutemenucontrols').slideDown();
				$('div#slhd_'+ref+'_mutecontrol').slideUp();
				$('h3#slhd_'+ref+'_activity_text').html('iTV met Marantz');
				break;
			case 5:		// Flubbertje
				$('div#slhd_'+ref+'_tvpresets').slideUp();
				$('div#slhd_'+ref+'_radiopresets').slideUp();
				$('div#slhd_'+ref+'_colorbuttons').slideUp();
				$('div#slhd_'+ref+'_videocontrols').slideUp();
				$('div#slhd_'+ref+'_updownleftrightcontrols').slideUp();
				$('div#slhd_'+ref+'_volumecontrols').slideDown();
				$('div#slhd_'+ref+'_exitguidecontrols').slideUp();
				$('div#slhd_'+ref+'_mutemenucontrols').slideUp();
				$('div#slhd_'+ref+'_mutecontrol').slideDown();
				$('h3#slhd_'+ref+'_activity_text').html('Flubbertje');
				break;
			case 4:		// Flubbertje muziek
				$('div#slhd_'+ref+'_tvpresets').slideUp();
				$('div#slhd_'+ref+'_radiopresets').slideUp();
				$('div#slhd_'+ref+'_colorbuttons').slideUp();
				$('div#slhd_'+ref+'_videocontrols').slideUp();
				$('div#slhd_'+ref+'_updownleftrightcontrols').slideUp();
				$('div#slhd_'+ref+'_volumecontrols').slideDown();
				$('div#slhd_'+ref+'_exitguidecontrols').slideUp();
				$('div#slhd_'+ref+'_mutemenucontrols').slideUp();
				$('div#slhd_'+ref+'_mutecontrol').slideDown();
				$('h3#slhd_'+ref+'_activity_text').html('Flubbertje muziek');
				break;
			case 3:		// Radio
				$('div#slhd_'+ref+'_tvpresets').slideUp();
				$('div#slhd_'+ref+'_radiopresets').slideDown();
				$('div#slhd_'+ref+'_colorbuttons').slideUp();
				$('div#slhd_'+ref+'_videocontrols').slideUp();
				$('div#slhd_'+ref+'_updownleftrightcontrols').slideUp();
				$('div#slhd_'+ref+'_volumecontrols').slideDown();
				$('div#slhd_'+ref+'_exitguidecontrols').slideUp();
				$('div#slhd_'+ref+'_mutemenucontrols').slideUp();
				$('div#slhd_'+ref+'_mutecontrol').slideDown();
				$('button#slhd_'+ref+'_radio').addClass('btn-info');
				$('button#slhd_'+ref+'_radio').removeClass('btn-outline-info');
				$('h3#slhd_'+ref+'_activity_text').html('Radio');
				break;
			case 2:		// TV kijken
				$('div#slhd_'+ref+'_tvpresets').slideDown();
				$('div#slhd_'+ref+'_radiopresets').slideUp();
				$('div#slhd_'+ref+'_colorbuttons').slideDown();
				$('div#slhd_'+ref+'_videocontrols').slideDown();
				$('div#slhd_'+ref+'_updownleftrightcontrols').slideDown();
				$('div#slhd_'+ref+'_volumecontrols').slideDown();
				$('div#slhd_'+ref+'_exitguidecontrols').slideDown();
				$('div#slhd_'+ref+'_mutemenucontrols').slideDown();
				$('div#slhd_'+ref+'_mutecontrol').slideUp();
				$('button#slhd_'+ref+'_tv').addClass('btn-warning');
				$('button#slhd_'+ref+'_tv').removeClass('btn-outline-warning');
				$('h3#slhd_'+ref+'_activity_text').html('TV kijken');
				break;
			case 1:		// PowerOff
				$('div#slhd_'+ref+'_tvpresets').slideUp();
				$('div#slhd_'+ref+'_radiopresets').slideUp();
				$('div#slhd_'+ref+'_colorbuttons').slideUp();
				$('div#slhd_'+ref+'_videocontrols').slideUp();
				$('div#slhd_'+ref+'_updownleftrightcontrols').slideUp();
				$('div#slhd_'+ref+'_volumecontrols').slideUp();
				$('div#slhd_'+ref+'_exitguidecontrols').slideUp();
				$('div#slhd_'+ref+'_mutemenucontrols').slideUp();
				$('div#slhd_'+ref+'_mutecontrol').slideUp();
				$('button#slhd_'+ref+'_off').addClass('btn-light');
				$('button#slhd_'+ref+'_off').removeClass('btn-outline-light');
				$('h3#slhd_'+ref+'_activity_text').html('UIT');
				break;
			default:
				$('div#slhd_'+ref+'_tvpresets').slideUp();
				$('div#slhd_'+ref+'_radiopresets').slideUp();
				$('div#slhd_'+ref+'_colorbuttons').slideUp();
				$('div#slhd_'+ref+'_videocontrols').slideUp();
				$('div#slhd_'+ref+'_updownleftrightcontrols').slideUp();
				$('div#slhd_'+ref+'_volumecontrols').slideUp();
				$('div#slhd_'+ref+'_exitguidecontrols').slideUp();
				$('div#slhd_'+ref+'_mutemenucontrols').slideUp();
				$('div#slhd_'+ref+'_mutecontrol').slideUp();
				$('h3#slhd_'+ref+'_activity_text').html('...');
				break;				
		}

	} else {
		// Element dows not exist, draw it
		console.log( timestamp() + " SplashHarmonyDevice.draw() - Drawing new element");

		var elStr = `<div class="col-lg-6" id="slhd_TOKEN_REF_ACTIVITY">
			<div class="card-box lh-card-box">
				<div class="lh-top">
					<div class="lh-logo">
						<img src="assets/images/LogitechHarmony.png">
					</div>
					<div class="lh-activity-box">
						<h3 id="slhd_TOKEN_REF_ACTIVITY_activity_text" class="m-t-2 m-b-5 p-b-2 text-light">...</h3>
						<h6 class="text-muted m-t-2">Activity</h6>
					</div>
					<div class="lh-refresh-box">
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_activity_refresh_button" class="slhd_color btn btn-outline-secondary waves-effect waves-light m-l-5 m-r-5" onclick="$('#slhd_TOKEN_REF_ACTIVITY_activity_refresh_button').addClass('btn-secondary');$('#slhd_TOKEN_REF_ACTIVITY_activity_refresh_button').removeClass('btn-outline-secondary'); $('#slhd_TOKEN_REF_ACTIVITY_activity_refresh').addClass('fa-spin'); CentralSplashUpdater.update( TOKEN_REF_ACTIVITY, HSUpdateHandler.uidt );"> <i id="slhd_TOKEN_REF_ACTIVITY_activity_refresh" class="fa fa-refresh m-l-5 m-r-5"> </i></button>
					</div>
				</div>
		
				<div>
					<div class="slhd_activity_wrapper">
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_tv" class="slhd_activity btn btn-outline-warning w-lg waves-effect waves-light font-13 text-center" onclick="SplashHSDeviceUpdate( TOKEN_REF_ACTIVITY, 2 );"> <i class="fa fa-tv"> </i><br>TV </button>
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_spotify" class="slhd_activity btn btn-outline-spotify w-lg waves-effect waves-light font-13 text-center" onclick="SplashHSDeviceUpdate( TOKEN_REF_ACTIVITY, 7 );"> <i class="fa fa-spotify"> </i><br>Gramofon </button>
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_radio" class="slhd_activity btn btn-outline-info w-lg waves-effect waves-light font-13 text-center" onclick="SplashHSDeviceUpdate( TOKEN_REF_ACTIVITY, 3 );"> <i class="fa fa-signal"> </i><br>Radio </button>
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_off" class="slhd_activity btn btn-outline-light w-lg waves-effect waves-dark font-13 text-center" onclick="SplashHSDeviceUpdate( TOKEN_REF_ACTIVITY, 1 );"> <i class="fa fa-power-off"> </i><br>Power </button>
					</div>
				</div>
		
				<div id="slhd_TOKEN_REF_ACTIVITY_videocontrols">
					<div class="slhd_videocontrol_wrapper">
						<button type="button" class="slhd_playpause btn btn-outline-secondary waves-effect waves-light m-l-5 m-r-5" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, 21 );"> <i class="fa fa-backward m-l-5 m-r-5"></i> </button>
						<button type="button" class="slhd_playpause btn btn-outline-secondary waves-effect waves-light m-l-5 m-r-5" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, 22 );"> <i class="fa fa-pause m-l-5 m-r-5"></i> </button>
						<button type="button" class="slhd_playpause btn btn-outline-secondary waves-effect waves-light m-l-5 m-r-5" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, 22 );"> <i class="fa fa-play m-l-5 m-r-5"></i> </button>
						<button type="button" class="slhd_playpause btn btn-outline-secondary waves-effect waves-light m-l-5 m-r-5" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, 20 );"> <i class="fa fa-stop m-l-5 m-r-5"></i> </button>
						<button type="button" class="slhd_playpause btn btn-outline-danger waves-effect waves-light m-l-5 m-r-5" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, 24 );"> <i class="fa fa-circle m-l-5 m-r-5"></i> </button>
						<button type="button" class="slhd_playpause btn btn-outline-secondary waves-effect waves-light m-l-5 m-r-5" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, 23 );"> <i class="fa fa-forward m-l-5 m-r-5"></i> </button>
					</div>
				</div>
				<div>
					<div class="slhd_preset_wrapper">
						<div class="btn-group-vertical m-b-10 m-t-10 m-l-10 m-r-10" id="slhd_TOKEN_REF_ACTIVITY_updownleftrightcontrols">
							<div class="btn-group">
								<button type="button" id="sehd_123_plus" class="btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, 18 );"> <i class="fa fa-angle-up fa-lg"></i> </button>
							</div>
							<div class="btn-group">
								<button type="button" class="btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, 16 );"> <i class="fa fa-angle-left fa-lg"></i> </button>
								<button type="button" class="btn btn-outline-secondary waves-effect waves-light pr-4" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, 19 );"> OK </button>
								<button type="button" class="btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, 17 );"> <i class="fa fa-angle-right fa-lg"></i> </button>
							</div>
							<div class="btn-group">
								<button type="button" class="btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, 15 );"> <i class="fa fa-angle-down fa-lg"></i> </button>
							</div>
						</div>
						<div class="btn-group-vertical">
							<div class="btn-group">
								<div class="btn-group-vertical m-10" id="slhd_TOKEN_REF_ACTIVITY_volumecontrols">
									<button type="button" class="btn btn-outline-secondary btn-sm waves-effect waves-light w-sm" id="slhd_TOKEN_REF_ACTIVITY_volumeUp"> <i class="fa fa-volume-up fa-lg ml-4 mr-4 mt-1 mb-1"></i> </button>
									<button type="button" class="btn btn-outline-secondary btn-sm waves-effect waves-light w-sm" id="slhd_TOKEN_REF_ACTIVITY_volumeDown"> <i class="fa fa-volume-down fa-lg ml-4 mr-4 mt-1 mb-1"> </i> </button>
								</div>
								<div style="width: 10px;">
								</div>
								<div class="btn-group-vertical m-10" id="slhd_TOKEN_REF_ACTIVITY_volumecontrols">
									<button type="button" class="btn btn-outline-secondary btn-sm waves-effect waves-light w-sm" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, 14 );"> <i class="fa fa-chevron-up fa-lg ml-4 mr-4 mt-1 mb-1"></i> </button>
									<button type="button" class="btn btn-outline-secondary btn-sm waves-effect waves-light w-sm" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, 13 );"> <i class="fa fa-chevron-down fa-lg ml-4 mr-4 mt-1 mb-1"> </i> </button>
								</div>
								<div style="width: 10px;">
								</div>
								<div class="btn-group-vertical m-10" id="slhd_TOKEN_REF_ACTIVITY_mutemenucontrols">
									<button type="button" class="btn btn-outline-secondary btn-sm waves-effect waves-light w-sm" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, 32 );"> <h5>Menu</h5> </button>
									<button type="button" class="btn btn-outline-secondary btn-sm waves-effect waves-light w-sm" id="slhd_TOKEN_REF_ACTIVITY_mute"> <h5><i class="fa fa-volume-off fa-lg mr-1"> </i> Mute</h5> </button>
								</div>
								<div class="btn-group-vertical m-10" id="slhd_TOKEN_REF_ACTIVITY_mutecontrol">
									<button type="button" class="btn btn-outline-secondary btn-sm waves-effect waves-light w-sm" id="slhd_TOKEN_REF_ACTIVITY_mute"> <h5><i class="fa fa-volume-off fa-lg mr-1"> </i> Mute</h5> </button>
								</div>
							</div>
							<div class="btn-group m-b-10 m-t-10 m-l-10 p-l-10" id="slhd_TOKEN_REF_ACTIVITY_exitguidecontrols" style="margin-bottom: 0px;">
								<button type="button" class="btn btn-outline-secondary waves-effect waves-light" style="margin-top: 5px; height: 35px;" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, 34 );"> <h5>Exit</h5> </button>
								<button type="button" class="btn btn-outline-secondary waves-effect waves-light" style="margin-top: 5px; height: 35px;" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, 32 );"> <h5>Guide</h5> </button>
							</div>
						</div>
					</div>
				</div>
		
				<div id="slhd_TOKEN_REF_ACTIVITY_tvpresets">
					<div class="slhd_preset_wrapper">
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_tvpreset_1" class="slhd_tvpreset btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 8, 8, 3 ] );"> <img src="assets/images/logo/npo-1-logo.png" style="height: 30px;"> </button>
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_tvpreset_2" class="slhd_tvpreset btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 8, 8, 4 ] );"> <img src="assets/images/logo/npo-2-logo.png" style="height: 30px;"> </button>
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_tvpreset_3" class="slhd_tvpreset btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 8, 8, 5 ] );"> <img src="assets/images/logo/npo-3-logo.png" style="height: 30px;"> </button>
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_tvpreset_4" class="slhd_tvpreset btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 8, 8, 6 ] );"> <img src="assets/images/logo/rtl4-logo.png" style="height: 30px;"> </button>
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_tvpreset_5" class="slhd_tvpreset btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 8, 8, 7 ] );"> <img src="assets/images/logo/rtl5-logo.png" style="height: 30px;"> </button>
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_tvpreset_6" class="slhd_tvpreset btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 8, 8, 9 ] );"> <img src="assets/images/logo/rtl7-logo.png" style="height: 30px;"> </button>
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_tvpreset_7" class="slhd_tvpreset btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 8, 9, 2 ] );"> <img src="assets/images/logo/rtl8-logo.png" style="height: 30px;"> </button>
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_tvpreset_8" class="slhd_tvpreset btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 8, 8, 8 ] );"> <img src="assets/images/logo/sbs6-logo.png" style="height: 30px;"> </button>
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_tvpreset_9" class="slhd_tvpreset btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 5, 6 ] );"> <img src="assets/images/logo/sbs9-logo.png" style="height: 30px;"> </button>
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_tvpreset_10" class="slhd_tvpreset btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 8, 8, 10 ] );"> <img src="assets/images/logo/net5-logo.png" style="height: 30px;"> </button>
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_tvpreset_11" class="slhd_tvpreset btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 8, 8, 11 ] );"> <img src="assets/images/logo/veronica_logo.png" style="padding-top: 7px; padding-bottom: 7px; width: 45px;"> </button>
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_tvpreset_12" class="slhd_tvpreset btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 3, 8 ] );"> <img src="assets/images/logo/national-geographic-logo.png" style="height: 30px;"> </button>
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_tvpreset_13" class="slhd_tvpreset btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 5, 7 ] );"> <img src="assets/images/logo/eurosport1.png" style="padding-top: 13px; padding-bottom: 13px; width: 42px;"> </button>
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_tvpreset_14" class="slhd_tvpreset btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 5, 8 ] );"> <img src="assets/images/logo/eurosport2.png" style="padding-top: 13px; padding-bottom: 13px; width: 42px;"> </button>
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_tvpreset_15" class="slhd_tvpreset btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 4, 10 ] );"> <img src="assets/images/logo/een-logo.png" style="height: 30px;"> </button>
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_tvpreset_16" class="slhd_tvpreset btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 4, 11 ] );"> <img src="assets/images/logo/canvas-logo.png" style="height: 30px;"> </button>
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_tvpreset_17" class="slhd_tvpreset btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 3, 7 ] );"> <img src="assets/images/logo/discovery-channel-logo.png" style="height: 30px;"> </button>
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_tvpreset_18" class="slhd_tvpreset btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 10, 7 ] );"> <img src="assets/images/logo/animal_planet_logo.png" style="width: 42px; height: 30px;"> </button>
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_tvpreset_19" class="slhd_tvpreset btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 4, 5, 5 ] );"> <img src="assets/images/logo/ziggo_sport_select_wit.png" style="width: 42px; height: 30px;"> </button>
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_tvpreset_20" class="slhd_tvpreset btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 4, 5, 8 ] );"> <img src="assets/images/logo/ziggo_sport_racing_wit.png" style="width: 42px; height: 30px;"> </button>

						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_tvpreset_20" class="slhd_tvpreset btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 3, 4 ] );"> <img src="assets/images/logo/Comedy_Central.png" style="width: 42px; height: 30px;"> </button>
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_tvpreset_20" class="slhd_tvpreset btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 3, 3 ] );"> <img src="assets/images/logo/RTL_Z_logo.png" style="width: 42px; height: 30px;"> </button>
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_tvpreset_20" class="slhd_tvpreset btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 4, 7 ] );"> <img src="assets/images/logo/BBC_First.png" style="width: 42px; height: 30px;"> </button>
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_tvpreset_20" class="slhd_tvpreset btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 4, 8 ] );"> <img src="assets/images/logo/BBC-One.png" style="width: 42px; height: 30px;"> </button>
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_tvpreset_20" class="slhd_tvpreset btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 4, 9 ] );"> <img src="assets/images/logo/BBC-Two.png" style="width: 42px; height: 30px;"> </button>
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_tvpreset_20" class="slhd_tvpreset btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 4, 2 ] );"> <img src="assets/images/logo/MTV_Logo.png" style="width: 42px; height: 30px;"> </button>
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_tvpreset_20" class="slhd_tvpreset btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 4, 6 ] );"> <img src="assets/images/logo/24Kitchen logo.png" style="width: 42px; height: 30px;"> </button>
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_tvpreset_20" class="slhd_tvpreset btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 5, 4 ] );"> <img src="assets/images/logo/history_channel.png" style="width: 42px; height: 30px;"> </button>
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_tvpreset_20" class="slhd_tvpreset btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 6, 1 ] );"> <img src="assets/images/logo/CNN.png" style="width: 42px; height: 30px;"> </button>
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_tvpreset_20" class="slhd_tvpreset btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 6, 2 ] );"> <img src="assets/images/logo/BBC_world_news_logo.png" style="width: 42px; height: 30px;"> </button>
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_tvpreset_20" class="slhd_tvpreset btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 6, 4 ] );"> <img src="assets/images/logo/al-jazeera-logo.png" style="width: 42px; height: 30px;"> </button>
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_tvpreset_20" class="slhd_tvpreset btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 9, 5 ] );"> <img src="assets/images/logo/RTL_Lounge_Logo.png" style="width: 42px; height: 30px;"> </button>
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_tvpreset_20" class="slhd_tvpreset btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 10, 5 ] );"> <img src="assets/images/logo/discovery_science.png" style="width: 42px; height: 30px;"> </button>
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_tvpreset_20" class="slhd_tvpreset btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 10, 8 ] );"> <img src="assets/images/logo/Travel_Channel.png" style="width: 42px; height: 30px;"> </button>
						<button type="button" id="slhd_TOKEN_REF_ACTIVITY_tvpreset_20" class="slhd_tvpreset btn btn-outline-secondary waves-effect waves-light" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 10, 9 ] );"> <img src="assets/images/logo/Nat_Geo_Wild.png" style="width: 42px; height: 30px;"> </button>

					</div>
				</div> 
				<div id="slhd_TOKEN_REF_ACTIVITY_colorbuttons">
					<div class="slhd_colorbutton_wrapper">
						<button type="button" class="slhd_color btn btn-danger waves-effect waves-light m-l-5 m-r-5" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, 29 );"> </button>
						<button type="button" class="slhd_color btn btn-success waves-effect waves-light m-l-5 m-r-5" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, 28 );"> </button>
						<button type="button" class="slhd_color btn btn-warning waves-effect waves-light m-l-5 m-r-5" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, 31 );"> </button>
						<button type="button" class="slhd_color btn btn-primary waves-effect waves-light m-l-5 m-r-5" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, 30 );"> </button>
					</div>
				</div>
		
				<div id="slhd_TOKEN_REF_ACTIVITY_radiopresets">
					<div class="slhd_preset_wrapper">
						<button type="button" id="slhd_radiopreset_1" class="slhd_radiopreset btn btn-outline-secondary waves-effect waves-dark" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 10, 2, 3 ] );"> <img src="assets/images/logo/NPO_Radio_1_logo.png" style="max-width: 42px; height: 30px;"> </button>
						<button type="button" id="slhd_radiopreset_2" class="slhd_radiopreset btn btn-outline-secondary waves-effect waves-dark" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 10, 2, 4 ] );"> <img src="assets/images/logo/NPO_Radio_2_logo.png" style="max-width: 42px; height: 30px;"> </button>
						<button type="button" id="slhd_radiopreset_3" class="slhd_radiopreset btn btn-outline-secondary waves-effect waves-dark" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 10, 2, 5 ] );"> <img src="assets/images/logo/NPO_3fm_logo.png" style="max-width: 42px; height: 30px;"> </button>
						<button type="button" id="slhd_radiopreset_4" class="slhd_radiopreset btn btn-outline-secondary waves-effect waves-dark" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 10, 2, 6 ] );"> <img src="assets/images/logo/NPO_Radio_4_logo.png" style="max-width: 42px; height: 30px;"> </button>
						<button type="button" id="slhd_radiopreset_5" class="slhd_radiopreset btn btn-outline-secondary waves-effect waves-dark" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 10, 2, 7 ] );"> <img src="assets/images/logo/NPO_Radio_5_logo.png" style="max-width: 42px; height: 30px;"> </button>
						<button type="button" id="slhd_radiopreset_6" class="slhd_radiopreset btn btn-outline-secondary waves-effect waves-dark" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 10, 2, 10 ] );"> <img src="assets/images/logo/sky-radio_logo.png" style="max-width: 42px; height: 30px;"> </button>
						<button type="button" id="slhd_radiopreset_7" class="slhd_radiopreset btn btn-outline-secondary waves-effect waves-dark" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 10, 2, 11 ] );"> <img src="assets/images/logo/538_logo.png" style="max-width: 42px; height: 30px;"> </button>
						<button type="button" id="slhd_radiopreset_8" class="slhd_radiopreset btn btn-outline-secondary waves-effect waves-dark" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 10, 3, 8 ] );"> <img src="assets/images/logo/slam_logo.png" style="max-width: 42px; height: 30px;"> </button>
						<button type="button" id="slhd_radiopreset_9" class="slhd_radiopreset btn btn-outline-secondary waves-effect waves-dark" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 10, 3, 11 ] );"> <img src="assets/images/logo/RadioVeronica_logo.png" style="max-width: 42px; height: 30px;"> </button>
						<button type="button" id="slhd_radiopreset_10" class="slhd_radiopreset btn btn-outline-secondary waves-effect waves-dark" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 10, 3, 3 ] );"> <img src="assets/images/logo/qmusic_logo.png" style="max-width: 42px; height: 30px;"> </button>
						<button type="button" id="slhd_radiopreset_11" class="slhd_radiopreset btn btn-outline-secondary waves-effect waves-dark" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 10, 3, 6 ] );"> <img src="assets/images/logo/ArrowClassicRock_logo.png" style="max-width: 42px; height: 30px;"> </button>
						<button type="button" id="slhd_radiopreset_12" class="slhd_radiopreset btn btn-outline-secondary waves-effect waves-dark" onclick="SplashHSDeviceUpdate( TOKEN_REF_TVRECEIVER, [ 10, 3, 7 ] );"> <img src="assets/images/logo/bnr_logo.png" style="max-width: 42px; height: 30px;"> </button>
					</div>
				</div> 
			</div> 
		</div>`;

		elStr = elStr.replace( /TOKEN_REF_ACTIVITY/g, ref );						// Homeseer device ref for Harmony activity device
		elStr = elStr.replace( /TOKEN_REF_TVRECEIVER/g, this.getTVReceiverRef() );	// Homeseer device ref for Harmony TV receiver device
		elStr = elStr.replace( /TOKEN_REF_TV/g, this.getTVRef() );					// Homeseer device ref for Harmony TV device
		elStr = elStr.replace( /TOKEN_REF_RECEIVER/g, this.getReceiverRef() );		// Homeseer device ref for Harmony Receiver device
		$( this.getBindingElement() ).append( elStr );

		$('div#slhd_'+ref+'_tvpresets').slideUp();
		$('div#slhd_'+ref+'_radiopresets').slideUp();
		$('div#slhd_'+ref+'_colorbuttons').slideUp();
		$('div#slhd_'+ref+'_videocontrols').slideUp();
		$('div#slhd_'+ref+'_updownleftrightcontrols').slideUp();
		$('div#slhd_'+ref+'_volumecontrols').slideUp();
		$('div#slhd_'+ref+'_exitguidecontrols').slideUp();
		$('div#slhd_'+ref+'_mutemenucontrols').slideUp();
		$('div#slhd_'+ref+'_mutecontrol').slideUp();

		var obj = this;

		$('button#slhd_'+ref+'_volumeUp').on("click", function () {
			console.log( timestamp() + " SplashHarmonyDevice.draw() - volumeUp click");
			obj.volumeUp();
		});
		$('button#slhd_'+ref+'_volumeDown').on("click", function () {
			console.log( timestamp() + " SplashHarmonyDevice.draw() - volumeDown click");
			obj.volumeDown();
		});
		$('button#slhd_'+ref+'_mute').on("click", function () {
			console.log( timestamp() + " SplashHarmonyDevice.draw() - mute click");
			obj.mute();
		});

		// Register for updates. Bind the callback to this object
		CentralSplashUpdater.register( ref, HSUpdateHandler, function() { obj.draw() } );
	}
}

SplashHarmonyDevice.prototype.volumeUp = function( ) {
	var hsDev = this.getHSDev();
	if ( [ 3, 7 ].includes(hsDev.getValue()) ) {				// Radio, Gramofon
		SplashHSDeviceUpdate( this.getReceiverRef(), 18 );		// Volume Up on Receiver [799]
	}
	if ( [ 2 ].includes(hsDev.getValue()) ) {					// TV Kijken
		SplashHSDeviceUpdate( this.getTVRef(), 16 );			// Volume Up on TV [801]
	}
}

SplashHarmonyDevice.prototype.volumeDown = function( ) {
	var hsDev = this.getHSDev();
	if ( [ 3, 7 ].includes(hsDev.getValue()) ) {				// Radio, Gramofon
		SplashHSDeviceUpdate( this.getReceiverRef(), 17 );		// Volume Down on Receiver [799]
	}
	if ( [ 2 ].includes(hsDev.getValue()) ) {					// TV Kijken
		SplashHSDeviceUpdate( this.getTVRef(), 15 );			// Volume Down on TV [801]
	}
}

SplashHarmonyDevice.prototype.mute = function( ) {
	var hsDev = this.getHSDev();
	if ( [ 3, 7 ].includes(hsDev.getValue()) ) {				// Radio, Gramofon
		SplashHSDeviceUpdate( this.getReceiverRef(), 16 );		// Mute on Receiver [799]
	}
	if ( [ 2 ].includes(hsDev.getValue()) ) {					// TV Kijken
		SplashHSDeviceUpdate( this.getTVRef(), 14 );			// Mute on TV [801]
	}
}

// ----------------------- Evohome Device Object ------------------------------------------
// Represents a Splash Evohome device
function SplashEvohomeZone ( locationId, zoneId ) {
	this.ehLocation = EHLocationFactory.create( locationId );
	this.ehZone = this.ehLocation.getZone( zoneId );
    // Element tot attach it to
    this.bindingElement = null;
	// Default width class. Works with col-lg-4 and col-lg-6
    this.widthClass = 'col-lg-4';
}

SplashEvohomeZone.prototype.getLocation = function( ) {
	return this.ehLocation;
}
SplashEvohomeZone.prototype.getZone = function( ) {
	return this.ehZone;
}
SplashEvohomeZone.prototype.setBindingElement = function( bindingElement ) {
	this.bindingElement = bindingElement;
}
SplashEvohomeZone.prototype.getBindingElement = function( ) {
	return this.bindingElement;
}
SplashEvohomeZone.prototype.setWidthClass = function( widthClass ) {
	this.widthClass = widthClass;
}
SplashEvohomeZone.prototype.getWidthClass = function( ) {
	return this.widthClass;
}

/*
 	blauw	class="text-info"		0-15,5
 	groen	class="text-success"	16-18,5
 	oranje	class="text-warning"	19-21,5
    rood	class="text-danger"		22+
*/

SplashEvohomeZone.prototype.draw = function() {
	console.log( timestamp() + " SplashEvohomeZone.draw()");
	var ehLocation = this.getLocation();
	var ehZone = this.getZone();
	var zoneId = ehZone.getZoneId();
	// Does the element exist? No: draw, Yes: update
	if ( $('div#sehd_'+zoneId).length ) {
		console.log( timestamp() + " SplashEvohomeZone.draw() - updating " + zoneId + " to temperature " + ehZone.getTemperature() + " and target " + ehZone.getTargetTemperature() );
		$('#sehd_'+zoneId+'_heat').text( ehZone.getTargetTemperature() ); 
		this.colorElementWithTemperature( '#sehd_'+zoneId+'_heat_tag', ehZone.getTargetTemperature() );
		this.colorElementWithTemperature( '#sehd_'+zoneId+'_temp_tag', ehZone.getTemperature() );
		$('#sehd_'+zoneId+'_temp').text( ehZone.getTemperature() ); 
		$('#sehd_'+zoneId+'_location').text( ehZone.getName() ); 
	} else {
		// Element dows not exist, draw it
		console.log( timestamp() + " SplashEvohomeZone.draw() - Drawing new element");

		var elStr = `<div class="TOKEN_WIDTH_CLASS" id="sehd_TOKEN_ZONEID">
			<div class="card-box eh-card-box">
				<div class="eh-logo">
					<img src="assets/images/honeywell-evohome-logo.png">
				</div>
				<div class="eh-heat-box">
					<h3 id="sehd_TOKEN_ZONEID_heat_tag" class="m-t-2 eh-heat-val">
						<b id="sehd_TOKEN_ZONEID_heat" class="counter">0</b>
						&#8451;
					</h3>
					<h6 class="text-muted eh-heat">Heatpoint</h6>
				</div>
				<div class="eh-temp-box">
					<h6 id="sehd_TOKEN_ZONEID_temp_tag" class="text-muted eh-temp-val">
						<b id="sehd_TOKEN_ZONEID_temp" class="counter">0</b>
						&#8451;
					</h6>
					<h6 class="text-muted eh-temp">Temp</h6>
				</div>
				<div>
					<label class="control-label m-t-30 m-l-5">
						<b id="sehd_TOKEN_ZONEID_location">--</b>
					</label>
				</div>
				<div class="btn-group m-b-10 m-t-10 m-l-10">
					<button type="button" id="sehd_TOKEN_ZONEID_5" class="sbrdb_late btn btn-outline-info btn-sm waves-effect waves-light">
						<span>5&#8451;</span>
					</button>
					<button type="button" id="sehd_TOKEN_ZONEID_15" class="sbrdb_late btn btn-outline-info btn-sm waves-effect waves-light">
						<span>15&#8451;</span>
					</button>
					<button type="button" id="sehd_TOKEN_ZONEID_17" class="sbrdb_late btn btn-outline-success btn-sm waves-effect waves-light">
						<span>17&#8451;</span>
					</button>
					<button type="button" id="sehd_TOKEN_ZONEID_20" class="sbrdb_late btn btn-outline-warning btn-sm waves-effect waves-light">
						<span>20&#8451;</span>
					</button><button type="button" id="sehd_TOKEN_ZONEID_21" class="sbrdb_late btn btn-outline-warning btn-sm waves-effect waves-light">
						<span>21&#8451;</span>
					</button><button type="button" id="sehd_TOKEN_ZONEID_22" class="sbrdb_late btn btn-outline-danger btn-sm waves-effect waves-light">
						<span>22&#8451;</span>
					</button>
				</div>
				<div class="btn-group-vertical m-b-10 eh-updown">
					<button type="button" id="sehd_TOKEN_ZONEID_plus" class="sbrdb_plus btn btn-light btn-sm waves-effect waves-light">
						<i class="fa fa-chevron-up"></i> 
					</button>
					<button type="button" id="sehd_TOKEN_ZONEID_min" class="sbrdb_min btn btn-outline-light btn-sm waves-effect waves-light">
						<i class="fa fa-chevron-down"> </i>
					</button>
				</div>
			</div>
		</div>`;

		elStr = elStr.replace( /TOKEN_WIDTH_CLASS/g, this.getWidthClass() );
		elStr = elStr.replace( /TOKEN_ZONEID/g, zoneId );
		$( this.getBindingElement() ).append( elStr );

		$('button#sehd_'+zoneId+'_5').on("click", function () {
			console.log( timestamp() + " SplashEvohomeZone.draw() - " + ehZone.getName() + " ["+zoneId+"] to 5");
			ehZone.setTargetTemperature( 5 );
			ThrottleSplashEHZoneSetpointUpdate( zoneId, 5, 'FollowSchedule', '' );
			CentralSplashUpdater.notify( EHUpdateHandler.uidt, ehLocation );
		});
		$('button#sehd_'+zoneId+'_15').on("click", function () {
			console.log( timestamp() + " SplashEvohomeZone.draw() - " + ehZone.getName() + " ["+zoneId+"] to 15");
			ehZone.setTargetTemperature( 15 );
			ThrottleSplashEHZoneSetpointUpdate( zoneId, 15, 'FollowSchedule', '' );
			CentralSplashUpdater.notify( EHUpdateHandler.uidt, ehLocation );
		});
		$('button#sehd_'+zoneId+'_17').on("click", function () {
			console.log( timestamp() + " SplashEvohomeZone.draw() - " + ehZone.getName() + " ["+zoneId+"] to 17");
			ehZone.setTargetTemperature( 17 );
			ThrottleSplashEHZoneSetpointUpdate( zoneId, 17, 'FollowSchedule', '' );
			CentralSplashUpdater.notify( EHUpdateHandler.uidt, ehLocation );
		});
		$('button#sehd_'+zoneId+'_20').on("click", function () {
			console.log( timestamp() + " SplashEvohomeZone.draw() - " + ehZone.getName() + " ["+zoneId+"] to 20");
			ehZone.setTargetTemperature( 20 );
			ThrottleSplashEHZoneSetpointUpdate( zoneId, 20, 'FollowSchedule', '' );
			CentralSplashUpdater.notify( EHUpdateHandler.uidt, ehLocation );
		});
		$('button#sehd_'+zoneId+'_21').on("click", function () {
			console.log( timestamp() + " SplashEvohomeZone.draw() - " + ehZone.getName() + " ["+zoneId+"] to 21");
			ehZone.setTargetTemperature( 21 );
			ThrottleSplashEHZoneSetpointUpdate( zoneId, 21, 'FollowSchedule', '' );
			CentralSplashUpdater.notify( EHUpdateHandler.uidt, ehLocation );
		});
		$('button#sehd_'+zoneId+'_22').on("click", function () {
			console.log( timestamp() + " SplashEvohomeZone.draw() - " + ehZone.getName() + " ["+zoneId+"] to 22");
			ehZone.setTargetTemperature( 22 );
			ThrottleSplashEHZoneSetpointUpdate( zoneId, 22, 'FollowSchedule', '' );
			CentralSplashUpdater.notify( EHUpdateHandler.uidt, ehLocation );
		});
		$('button#sehd_'+zoneId+'_plus').on("click", function () {
			var heatpoint = Math.min( parseFloat( $('b#sehd_'+zoneId+'_heat').text() ) + .5, 25 );
			console.log( timestamp() + " SplashEvohomeZone.draw() - " + ehZone.getName() + " ["+zoneId+"] Plus to " + heatpoint);
			ehZone.setTargetTemperature( heatpoint );
			ThrottleSplashEHZoneSetpointUpdate( zoneId, heatpoint, 'FollowSchedule', '' );
			CentralSplashUpdater.notify( EHUpdateHandler.uidt, ehLocation );
		});
		$('button#sehd_'+zoneId+'_min').on("click", function () {
			var heatpoint = Math.max( parseFloat(  $('b#sehd_'+zoneId+'_heat').text() ) - .5, 5 );
			console.log( timestamp() + " SplashEvohomeZone.draw() - " + ehZone.getName() + " ["+zoneId+"] Min to " + heatpoint);
			ehZone.setTargetTemperature( heatpoint );
			ThrottleSplashEHZoneSetpointUpdate( zoneId, heatpoint, 'FollowSchedule', '' );
			CentralSplashUpdater.notify( EHUpdateHandler.uidt, ehLocation );
		});
		// Register for updates. Bind the callback to this object
		var obj = this;
		CentralSplashUpdater.register( ehLocation.getLocationId(), EHUpdateHandler, function() { obj.draw() } );
	}

}

/*
 	blauw	class="text-info"		0-15,5
 	groen	class="text-success"	16-18,5
 	oranje	class="text-warning"	19-21,5
    rood	class="text-danger"		22+
*/
SplashEvohomeZone.prototype.colorElementWithTemperature = function( el, temp ) {
	if ( temp > 21.5 ) {
		// red
		$( el ).addClass( 'text-danger' ); 
		$( el ).removeClass( 'text-warning' ); 
		$( el ).removeClass( 'text-success' ); 
		$( el ).removeClass( 'text-info' ); 
	} else if ( temp > 18.5 ) {
		// orange
		$( el ).addClass( 'text-warning' ); 
		$( el ).removeClass( 'text-danger' ); 
		$( el ).removeClass( 'text-success' ); 
		$( el ).removeClass( 'text-info' ); 
	} else if ( temp > 15.5 ) {
		// green
		$( el ).addClass( 'text-success' ); 
		$( el ).removeClass( 'text-danger' ); 
		$( el ).removeClass( 'text-warning' ); 
		$( el ).removeClass( 'text-info' ); 
	} else {
		// blue
		$( el ).addClass( 'text-info' ); 
		$( el ).removeClass( 'text-danger' ); 
		$( el ).removeClass( 'text-warning' ); 
		$( el ).removeClass( 'text-success' ); 
	}
}

// ----------------------- Bedroom Device Object ------------------------------------------
// Represents a Splash Bedroom device combo
function SplashBedroomDevice ( ) {
    // Element tot attach it to
    this.bindingElement = null;
	// Default width class. Works with col-lg-4, col-lg-6 and col-12
    this.widthClass = 'col-lg-6';
}

SplashBedroomDevice.prototype.setBindingElement = function( bindingElement ) {
	this.bindingElement = bindingElement;
}
SplashBedroomDevice.prototype.getBindingElement = function( ) {
	return this.bindingElement;
}
SplashBedroomDevice.prototype.setWidthClass = function( widthClass ) {
	this.widthClass = widthClass;
}
SplashBedroomDevice.prototype.getWidthClass = function( ) {
	return this.widthClass;
}

SplashBedroomDevice.prototype.draw = function( ) {
	console.log( timestamp() + " SplashBedroomDevice.draw()");
	var hsDev = HSDeviceFactory.create( 598 );
	// Does the element exist? No: draw, Yes: update
	if ( $('div#sbrd').length ) {
		console.log( timestamp() + " SplashBedroomDevice.draw() - Update the element");

		// Update the slider, and potentially enable it, if this is the first update
    	var $range = $("#sbrd_slider");
    	var slider = $range.data("ionRangeSlider");
		// Is it different?
		console.log( timestamp() + " SplashBedroomDevice.draw() - slider.result.from: " + slider.result.from );

		var hsd598 = HSDeviceFactory.create( 598 );			// Wandlampen
		
		if ( slider.result.from != hsd598.getValue() ) {
			console.log( timestamp() + " SplashBedroomDevice.draw() - updating actual slider" );
	        slider.update({
	            from: Math.min(hsd598.getValue(), 100),
		        disable: false
	        });
		};

	} else {
		// Element dows not exist, draw it
		console.log( timestamp() + " SplashBedroomDevice.draw() - Drawing new element");

		var elStr = `<div class="TOKEN_WIDTH_CLASS" id="sbrd">
			<div class="card-box">
				<form class="form-horizontal">
					<div class="form-group">
						<label for="slrd_slider" class="control-label">
							<b>Slaapkamer</b>
							<span class="font-normal text-muted clearfix">dimmer</span>
						</label>
						<div class="m-b-20">
							<input type="text" id="sbrd_slider">
						</div>
						<div>
							<div class="sbrdb_activity_wrapper">
								<div class="btn-group m-b-10">
									<button type="button" class="sbrdb_on btn btn-light waves-effect">
										<i class="fa fa-toggle-on m-r-5"></i>
										<span>Aan</span>
									</button>
									<button type="button" class="sbrdb_off btn btn-outline-light waves-effect waves-dark">
										<i class="fa  fa-toggle-off m-r-5"></i>
										<span>Uit</span>
									</button>
								</div>
								&nbsp;
								<div class="btn-group m-b-10">
									<button type="button" class="sbrdb_plus btn btn-light waves-effect waves-light">
										<i class="fa fa-chevron-up m-r-5"></i> 
									</button>
									<button type="button" class="sbrdb_min btn btn-outline-light waves-effect waves-light">
									<i class="fa fa-chevron-down m-r-5"> </i>
									</button>
								</div>
								&nbsp;								
								<div class="btn-group m-b-10">
									<button type="button" class="sbrdb_late btn btn-outline-info waves-effect waves-light">
										<i class="fa fa-television m-r-5"></i>
										<span>Laat</span>
									</button>
								</div>
								&nbsp;
								<div class="btn-group m-b-10">
									<button type="button" class="sbrdb_bright btn btn-outline-danger waves-effect waves-light">
										<i class="fa fa-sun-o m-r-5"></i>
										<span>Bright</span>
									</button>
								</div>
							</div>
						</div> 
					</div>
				</form>
			</div>
		</div>`;

		elStr = elStr.replace( /TOKEN_WIDTH_CLASS/g, this.getWidthClass() );
		$( this.getBindingElement() ).append( elStr );

		var sbrdObj = this;
		$("button.sbrdb_on").on("click", function () {
			var $range = $("#sbrd_slider");
			var slider = $range.data("ionRangeSlider");
		    slider.update({
		        from: 25
		    });
		    sbrdObj.setValue( 25 );
		});
		$("button.sbrdb_off").on("click", function () {
			var $range = $("#sbrd_slider");
			var slider = $range.data("ionRangeSlider");
		    slider.update({
		        from: 0
		    });
		    sbrdObj.setValue( 0 );
		});
		$("button.sbrdb_plus").on("click", function () {
			var $range = $("#sbrd_slider");
			var slider = $range.data("ionRangeSlider");
			var nv = Math.min(slider.result.from + 10, 100);
		    slider.update({
		        from: nv
		    });
		    sbrdObj.setValue( nv );
		});
		$("button.sbrdb_min").on("click", function () {
			var $range = $("#sbrd_slider");
			var slider = $range.data("ionRangeSlider");
			var nv = Math.max(slider.result.from - 10, 0);
		    slider.update({
		        from: nv
		    });
		    sbrdObj.setValue( nv );
		});
		$("button.sbrdb_late").on("click", function () {
			var $range = $("#sbrd_slider");
			var slider = $range.data("ionRangeSlider");
		    slider.update({
		        from: 1
		    });
		    sbrdObj.setValue( 1 );
		});
		$("button.sbrdb_bright").on("click", function () {
			var $range = $("#sbrd_slider");
			var slider = $range.data("ionRangeSlider");
		    slider.update({
		        from: 99
		    });
		    sbrdObj.setValue( 99 );
		});

		var $range = $("#sbrd_slider");          
	    $range.ionRangeSlider({
	        type: "single",
			grid: true,
	        min: 0,
	        max: 100,
	        hide_min_max: true,
	        hide_from_to: false,
	        from: 44,
	        disable: false,
	        keyboard: true,
	        onStart: function (data) {
				console.log( timestamp() + ' ---> Slider Bedroom started');
	        },
	        onChange: function (data) {
				console.log( timestamp() + ' ---> Slider Bedroom changed to ' + data.from);
			    slrdObj.setValue( data.from );
	        },
	        onFinish: function (data) {
	        	console.log( timestamp() + ' ---> Slider Bedroom finished on ' + data.from);
	        },
	        onUpdate: function (data) {
				console.log( timestamp() + ' ---> Slider Bedroom updated');
	        }
	    });
		// Register for updates. Bind the callback to this object
		var obj = this;
		CentralSplashUpdater.register( 598, HSUpdateHandler, function() { obj.draw() } );
		
	}

}

SplashBedroomDevice.prototype.setValue = function( value ) {
	var hsDev = HSDeviceFactory.create( 598 );
	hsDev.setValue( value );
	ThrottleSplashHSDeviceUpdate( 598, value );						// Wandlampen
	CentralSplashUpdater.notify( HSUpdateHandler.uidt, hsDev );
}

// ----------------------- Livingroom Device Object ------------------------------------------
// Represents a Splash Livingroom device combo
function SplashLivingroomDevice ( ) {
    // Element tot attach it to
    this.bindingElement = null;
	// Default width class. Works with col-lg-4, col-lg-6 and col-12
    this.widthClass = 'col-lg-6';
}

SplashLivingroomDevice.prototype.setBindingElement = function( bindingElement ) {
	this.bindingElement = bindingElement;
}
SplashLivingroomDevice.prototype.getBindingElement = function( ) {
	return this.bindingElement;
}
SplashLivingroomDevice.prototype.setWidthClass = function( widthClass ) {
	this.widthClass = widthClass;
}
SplashLivingroomDevice.prototype.getWidthClass = function( ) {
	return this.widthClass;
}

// Value
//  0-10% : dim the lights, switches off
//  > 10% : switches on
//  
SplashLivingroomDevice.prototype.draw = function( ) {
	console.log( timestamp() + " SplashLivingroomDevice.draw()");
	var hsDev = HSDeviceFactory.create( 298 );
	// Does the element exist? No: draw, Yes: update
	if ( $('div#slrd').length ) {
		console.log( timestamp() + " SplashLivingroomDevice.draw() - Update the element");
		// Update the slider, and potentially enable it, if this is the first update
    	var $range = $("#slrd_slider");
    	var slider = $range.data("ionRangeSlider");
		// Is it different?
		console.log( timestamp() + " SplashLivingroomDevice.draw() - slider.result.from: " + slider.result.from );

		var hsd298 = HSDeviceFactory.create( 298 );			// Buislamp
		var hsd377 = HSDeviceFactory.create( 377 );			// Touchlamp
		var hsd422 = HSDeviceFactory.create( 422 );			// Tripodlamp
		var hsd738 = HSDeviceFactory.create( 738 );			// Vlechtlamp
		var hsd441 = HSDeviceFactory.create( 441 );			// Keuken plafondspots
		var hsd508 = HSDeviceFactory.create( 508 );			// Gang designlamp
		var hsd814 = HSDeviceFactory.create( 814 );			// Eetafel plafondlamp

		var value = Math.round( ( hsd298.getValue() + hsd422.getValue() ) / 2 );
		value = Math.max( value, ( hsd377.getValue() > 0 ? 10 : 0 ) );
		value = Math.max( value, ( hsd738.getValue() > 0 ? 20 : 0 ) );
		value = Math.max( value, ( hsd508.getValue() > 0 ? 10 : 0 ) );
		
		if ( slider.result.from != value ) {
			console.log( timestamp() + " SplashLivingroomDevice.draw() - updating actual slider" );
	        slider.update({
	            from: Math.min(value, 100),
		        disable: false
	        });
		};

	} else {
		// Element dows not exist, draw it
		console.log( timestamp() + " SplashLivingroomDevice.draw() - Drawing new element");
		// col-12 
//		$( this.getBindingElement() ).append('<div class="' + this.getWidthClass() + '" id="slrd"><div class="card-box"><form class="form-horizontal"><div class="form-group"><label for="slrd_slider" class="control-label"><b>Woonkamer</b> <span class="font-normal text-muted clearfix">dimmer</span></label><div class="m-b-20"><input type="text" id="slrd_slider"></div><div><div class="slrdb_activity_wrapper"><div class="btn-group m-b-10"><button type="button" id="slrdb_on" class="slrdb_on btn btn-light waves-effect"> <i class="fa fa-toggle-on m-r-5"></i> <span>Aan</span></button><button type="button" id="slrdb_off" class="slrdb_off btn btn-outline-light waves-effect waves-dark"> <i class="fa fa-toggle-off m-r-5"></i> <span>Uit</span></button></div>&nbsp;<div class="btn-group m-b-10"><button type="button" id="slrdb_plus" class="slrdb_plus btn btn-light waves-effect waves-light"> <i class="fa fa-chevron-up m-r-5"></i> </button><button type="button" id="slrdb_min" class="slrdb_min btn btn-outline-light waves-effect waves-light"> <i class="fa fa-chevron-down m-r-5"> </i> </button></div>&nbsp;<div class="btn-group m-b-10"><button type="button" id="slrdb_movie" class="slrdb_movie btn btn-outline-info waves-effect waves-light"><i class="fa fa-television m-r-5"></i> <span>Film</span></button><button type="button" id="slrdb_entertain" class="slrdb_entertain btn btn-outline-success waves-effect waves-light"><i class="fa fa-comments m-r-5"></i> <span>Visite</span></button><button type="button" id="slrdb_kook" class="slrdb_kook btn btn-outline-warning waves-effect waves-light"><i class="fa fa-search m-r-5"></i> <span>Koken</span></button><button type="button" id="slrdb_bright" class="slrdb_bright btn btn-outline-danger waves-effect waves-light"><i class="fa fa-sun-o m-r-5"></i> <span>Bright</span></button></div></div></div> </div></form></div></div>');

		var elStr = `<div class="TOKEN_WIDTH_CLASS" id="slrd">
			<div class="card-box">
				<form class="form-horizontal">
					<div class="form-group">
						<label for="slrd_slider" class="control-label">
							<b>Woonkamer</b> 
							<span class="font-normal text-muted clearfix">dimmer</span>
						</label>
						<div class="m-b-20">
							<input type="text" id="slrd_slider">
						</div>
						<div>
							<div class="slrdb_activity_wrapper">
								<div class="btn-group m-b-10">
									<button type="button" id="slrdb_on" class="slrdb_on btn btn-light waves-effect w-xs font-13 text-center"> 
										<i class="fa fa-toggle-on m-r-5"></i> 
										<span>Aan</span>
									</button>
									<button type="button" id="slrdb_off" class="slrdb_off btn btn-outline-light waves-effect waves-dark w-xs font-13 text-center"> 
										<i class="fa fa-toggle-off m-r-5"></i> 
										<span>Uit</span>
									</button>
								</div>
								&nbsp;
								<div class="btn-group m-b-10">
									<button type="button" id="slrdb_plus" class="slrdb_plus btn btn-light waves-effect waves-light w-xs font-13 text-center"> 
										<i class="fa fa-chevron-up m-r-5"></i> 
									</button>
									<button type="button" id="slrdb_min" class="slrdb_min btn btn-outline-light waves-effect waves-light w-xs font-13 text-center"> 
										<i class="fa fa-chevron-down m-r-5"> </i> 
									</button>
								</div>
							</div>
						</div>
						<div>
							<div class="slrdb_activity_wrapper">
								<div class="btn-group m-b-10">
									<button type="button" id="slrdb_movie" class="slrdb_movie btn btn-outline-info waves-effect waves-light font-13 text-center">
										<i class="fa fa-television m-r-5"></i> 
										<span>Film</span>
									</button>
								</div>
								&nbsp;
								<div class="btn-group m-b-10">
									<button type="button" id="slrdb_entertain" class="slrdb_entertain btn btn-outline-success waves-effect waves-light font-13 text-center">
										<i class="fa fa-comments m-r-5"></i> 
										<span>Visite</span>
									</button>
								</div>
								&nbsp;
								<div class="btn-group m-b-10">
									<button type="button" id="slrdb_kook" class="slrdb_kook btn btn-outline-warning waves-effect waves-light font-13 text-center">
										<i class="fa fa-search m-r-5"></i> 
										<span>Koken</span>
									</button>
								</div>
								&nbsp;
								<div class="btn-group m-b-10">
									<button type="button" id="slrdb_dinner" class="slrdb_dinner btn btn-outline-primary waves-effect waves-light font-13 text-center">
										<i class="fa fa-leaf m-r-5"></i> 
										<span>Dinner</span>
									</button>
								</div>
								&nbsp;
								<div class="btn-group m-b-10">
									<button type="button" id="slrdb_bright" class="slrdb_bright btn btn-outline-danger waves-effect waves-light font-13 text-center">
										<i class="fa fa-sun-o m-r-5"></i> 
										<span>Bright</span>
									</button>
								</div>
							</div>
						</div> 
					</div>
				</form>
			</div>
		</div>`;

		elStr = elStr.replace( /TOKEN_WIDTH_CLASS/g, this.getWidthClass() );	// 
		$( this.getBindingElement() ).append( elStr );

		var slrdObj = this;
		$("button#slrdb_on").on("click", function () {
			var $range = $("#slrd_slider");
			var slider = $range.data("ionRangeSlider");
		    slider.update({
		        from: 50
		    });
			var specificValues = { 441: 20,  814: 2 };	// Set the Kitchen lights to 20, the Eetafel plafondlamp lights to 2
		    setHSLivingroomDevices( 50, true, specificValues );
		});
		$("button#slrdb_off").on("click", function () {
			var $range = $("#slrd_slider");
			var slider = $range.data("ionRangeSlider");
		    slider.update({
		        from: 0
		    });
		    setHSLivingroomDevices( 0 );
		    // Also switch lights in the garden off
			setValueForHSDevice( 824, 0, true );	// Gevellamp tuin
			setValueForHSDevice( 826, 0, true );	// Gevelelektra tuin
			setValueForHSDevice( 837, 0, true );	// Tuinkabel tuin
		});
		$("button#slrdb_movie").on("click", function () {
			var $range = $("#slrd_slider");
			var slider = $range.data("ionRangeSlider");
		    slider.update({
		        from: 40
		    });
			var specificValues = { 441: 20,  814: 2 };	// Set the Kitchen lights to 20, the Eetafel plafondlamp lights to 2
		    setHSLivingroomDevices( 40, true, specificValues );
		});
		$("button#slrdb_entertain").on("click", function () {
			var $range = $("#slrd_slider");
			var slider = $range.data("ionRangeSlider");
		    slider.update({
		        from: 50
		    });
			var specificValues = { 441: 20,  814: 2 };	// Set the Kitchen lights to 20, the Eetafel plafondlamp lights to 2
		    setHSLivingroomDevices( 50, true, specificValues );
		});
		$("button#slrdb_kook").on("click", function () {
			var $range = $("#slrd_slider");
			var slider = $range.data("ionRangeSlider");
		    slider.update({
		        from: 60
		    });
			var specificValues = { 441: 60,  814: 2 };	// Set the Kitchen lights to 60, the Eetafel plafondlamp lights to 2
		    setHSLivingroomDevices( 50, true, specificValues );
		});
		$("button#slrdb_dinner").on("click", function () {
			var $range = $("#slrd_slider");
			var slider = $range.data("ionRangeSlider");
		    slider.update({
		        from: 50
		    });
			var specificValues = { 441: 20,  814: 50 };	// Set the Kitchen lights to 20, the Eetafel plafondlamp lights to 50
		    setHSLivingroomDevices( 50, true, specificValues );
		});
		$("button#slrdb_bright").on("click", function () {
			var $range = $("#slrd_slider");
			var slider = $range.data("ionRangeSlider");
		    slider.update({
		        from: 100
		    });
		    setHSLivingroomDevices( 99 );
		});
		$("button#slrdb_plus").on("click", function () {
			var $range = $("#slrd_slider");
			var slider = $range.data("ionRangeSlider");
			var nv = Math.min(slider.result.from + 10, 100);
		    slider.update({
		        from: nv
		    });
			var hsd441 = HSDeviceFactory.create( 441 );			// Keuken plafondspots
			var hsd814 = HSDeviceFactory.create( 814 );			// Eetafel plafondlamp
			// Set the Kitchen lights +5, the Eetafel plafondlamp lights +5
			var specificValues = { 441: Math.min((hsd441.getValue() + 5), 100),  814: Math.min((hsd814.getValue() + 5), 100) };
		    setHSLivingroomDevices( nv, true, specificValues );
		});
		$("button#slrdb_min").on("click", function () {
			var $range = $("#slrd_slider");
			var slider = $range.data("ionRangeSlider");
			var nv = Math.max(slider.result.from - 10, 0);
		    slider.update({
		        from: nv
		    });
			var hsd441 = HSDeviceFactory.create( 441 );			// Keuken plafondspots
			var hsd814 = HSDeviceFactory.create( 814 );			// Eetafel plafondlamp
			// Set the Kitchen lights -5, the Eetafel plafondlamp lights -5
			var specificValues = { 441: Math.max((hsd441.getValue() - 5), 0),  814: Math.max((hsd814.getValue() - 5), 0) };
		    setHSLivingroomDevices( nv, true, specificValues );
		    setHSLivingroomDevices( nv );
		});
		var $range = $("#slrd_slider");          
	    $range.ionRangeSlider({
	        type: "single",
			grid: true,
	        min: 0,
	        max: 100,
	        hide_min_max: true,
	        hide_from_to: false,
	        from: 44,
	        disable: false,
	        keyboard: true,
	        onStart: function (data) {
				console.log( timestamp() + ' ---> Slider Livingroom started');
	        },
	        onChange: function (data) {
				console.log( timestamp() + ' ---> Slider Livingroom changed to ' + data.from);
			    setHSLivingroomDevices( data.from, false );
	        },
	        onFinish: function (data) {
	        	console.log( timestamp() + ' ---> Slider Livingroom finished on ' + data.from);
				if ( data.from == 0 ) {
				    // Also switch lights in the garden off
					setValueForHSDevice( 824, 0, true );	// Gevellamp tuin
					setValueForHSDevice( 826, 0, true );	// Gevelelektra tuin
					setValueForHSDevice( 837, 0, true );	// Tuinkabel tuin
				}
	        },
	        onUpdate: function (data) {
				console.log( timestamp() + ' ---> Slider Livingroom updated');
	        }
	    });
		// Register for updates. Bind the callback to this object
		var obj = this;
		CentralSplashUpdater.register( 298, HSUpdateHandler, function() { obj.draw() } );	// Woonkamer Buislamp
		CentralSplashUpdater.register( 377, HSUpdateHandler, function() { obj.draw() } );	// Woonkamer Kleurenlamp
		CentralSplashUpdater.register( 422, HSUpdateHandler, function() { obj.draw() } );	// Woonkamer tripodlamp
		CentralSplashUpdater.register( 441, HSUpdateHandler, function() { obj.draw() } );	// Keuken plafondspots
		CentralSplashUpdater.register( 508, HSUpdateHandler, function() { obj.draw() } );	// Gang Designlamp
		CentralSplashUpdater.register( 738, HSUpdateHandler, function() { obj.draw() } );	// Woonkamer Vlechtlamp
		CentralSplashUpdater.register( 814, HSUpdateHandler, function() { obj.draw() } );	// Woonkamer Eettafel		
	}
}

// Specific values can contain an array with special values per ref. The slides does not work that way, but the buttons can.
function setHSLivingroomDevices( value, notify = true, specificValues = null ) {
	var devArray = [ 298, 377, 422, 441, 508, 738, 814 ];
	
	$.each( devArray, function( index, ref ) {
		var deviceValue = value;				
		if ( specificValues != null && specificValues[ ref ] != 'undefined' && (specificValues[ ref ] === parseInt(specificValues[ ref ], 10)) ) {
			// Specific value requested
			deviceValue = specificValues[ ref ];				
		} else {
			// calculate value
			switch( ref ) {
				case 377:	// Touchlamp - On/Off
					deviceValue = ( value > 10 ? 255 : 0 );
					break;
				case 738:	// Vlechtlamp
					deviceValue = ( value > 20 ? 255 : 0 );
					break;
				case 441:	// Keuken plafondspots
					deviceValue = ( value < 40 ? Math.round( value / 3 ) : ( value < 60 ? Math.round( value / 2 ) : value ) );
					break;
				case 508:	// Gang designlamp
					deviceValue = ( value == 99 ? 99 : ( value < 60 ? ( value == 0 ? 0 : 5 ) : 10 ) );
					break;
				case 814:	// Eetafel plafondlamp
					deviceValue = ( value < 40 ? Math.round( value / 3 ) : ( value < 60 ? Math.round( value / 2 ) : value ) );
					break;
				case 298:	// Buislamp - value = value
				case 422:	// Tripodlamp
				default:
			}
		}
		setValueForHSDevice( ref, deviceValue, notify );
	});
}

// Specific values can contain an array with special values per ref. The slides does not work that way, but the buttons can.
function setValueForHSDevice( ref, value, notify = true ) {
	var hsd = HSDeviceFactory.create( ref );
	hsd.setValue( value );
	if ( notify ) { CentralSplashUpdater.notify( HSUpdateHandler.uidt, hsd ); }
	ThrottleSplashHSDeviceUpdate( ref, value );
}
// ----------------------- Temperature Device Object ------------------------------------------
// Represents a Splash Temperature device

function SplashTempDevice ( ref ) {
    this.hsdev = HSDeviceFactory.create( ref );
    // Element tot attach it to
    this.bindingElement = null;
}

SplashTempDevice.prototype.getHSDev = function( ) {
	return this.hsdev;
}
SplashTempDevice.prototype.setBindingElement = function( bindingElement ) {
	this.bindingElement = bindingElement;
}
SplashTempDevice.prototype.getBindingElement = function( ) {
	return this.bindingElement;
}

SplashTempDevice.prototype.draw = function( ) {
	console.log( timestamp() + " SplashTempDevice.draw()");
	var hsDev = this.getHSDev();
	var ref = hsDev.getRef();
	// Does the element exist? No: draw, Yes: update
	if ( $('div#std_' + ref).length ) {
		console.log( timestamp() + " SplashTempDevice.draw() - Update element [ " + ref + " ] to " + hsDev.getValue());

		if ( $('h3#std_' + ref + '_status .counter').text() != hsDev.getValue() ) {
			$('h3#std_' + ref + '_status').html( '<b class="counter">'+hsDev.getValue()+'</b>&#8451;' );
			if ( hsDev.getValue() > 0 ) {
				try {
					$('h3#std_' + ref + '_status .counter').counterUp({
    					delay: 100,
					    time: 1200
				    });
				}
				catch(error) {
					console.log(error);
				}
			}
		}

		$('h7#std_' + ref + '_name').text( hsDev.getName() );
		$('p#std_' + ref + '_location').text( hsDev.getLocation() );

		$('std_'+ref+'_thermometer').removeClass('fa-thermometer-full');
		$('std_'+ref+'_thermometer').removeClass('fa-thermometer-three-quarters');
		$('std_'+ref+'_thermometer').removeClass('fa-thermometer-half');
		$('std_'+ref+'_thermometer').removeClass('fa-thermometer-quarter');
		$('std_'+ref+'_thermometer').removeClass('fa-thermometer-empty');

		$('std_'+ref+'_bg-icon').removeClass('bg-icon-danger');
		$('std_'+ref+'_bg-icon').removeClass('bg-icon-warning');
		$('std_'+ref+'_bg-icon').removeClass('bg-icon-success');
		$('std_'+ref+'_bg-icon').removeClass('bg-icon-info');
		$('std_'+ref+'_bg-icon').removeClass('bg-icon-primary');

		$('std_'+ref+'_status').removeClass('text-danger');
		$('std_'+ref+'_status').removeClass('text-warning');
		$('std_'+ref+'_status').removeClass('text-success');
		$('std_'+ref+'_status').removeClass('text-info');
		$('std_'+ref+'_status').removeClass('text-primary');

		if (hsDev.getValue() > 25) {
			// rood
			$('std_'+ref+'_thermometer').addClass('fa-thermometer-full');
			$('std_'+ref+'_status').addClass('text-danger');
			$('std_'+ref+'_bg-icon').addClass('bg-icon-danger');
		} else if (hsDev.getValue() > 13) {
			// geel
			$('std_'+ref+'_thermometer').addClass('fa-thermometer-three-quarters');
			$('std_'+ref+'_status').addClass('text-warning');
			$('std_'+ref+'_bg-icon').addClass('bg-icon-warning');
		} else if (hsDev.getValue() > 5) {
			// groen
			$('std_'+ref+'_thermometer').addClass('fa-thermometer-half');
			$('std_'+ref+'_status').addClass('text-success');
			$('std_'+ref+'_bg-icon').addClass('bg-icon-success');
		} else if (hsDev.getValue() > 0) {
			// blauw
			$('std_'+ref+'_thermometer').addClass('fa-thermometer-quarter');
			$('std_'+ref+'_status').addClass('text-info');
			$('std_'+ref+'_bg-icon').addClass('bg-icon-info');
		} else {
			// blauw
			$('std_'+ref+'_thermometer').addClass('fa-thermometer-empty');
			$('std_'+ref+'_status').addClass('text-primary');
			$('std_'+ref+'_bg-icon').addClass('bg-icon-primary');
		}		

	} else {
		// Element dows not exist, draw it
		console.log( timestamp() + " SplashTempDevice.draw() - Drawing new element");
		$( this.getBindingElement() ).append('<div class="col-lg-3 col-md-6" id="std_'+ref+'"><div class="widget-bg-color-icon card-box"><div id="std_'+ref+'_bg-icon" class="bg-icon bg-icon-warning pull-left"><i id="std_'+ref+'_thermometer" class="fa fa-thermometer-empty text-primary"></i></div><div class="text-right"><h3 id="std_'+ref+'_status" class="text-primary m-t-10">--%</h3><h7 id="std_'+ref+'_name" class="text-dark m-t-10">--</h7><p id="std_'+ref+'_location" class="text-muted mb-0 blockquote-reverse">--</p><div class="clearfix"></div></div></div>');

		// Onclick toggle the uptime
		$('p#std_' + ref + '_location').slideUp();	// default slideup
		$('div#std_'+ref).click( function(e) {
			$('p#std_' + ref + '_location').slideToggle();	// slideUp/ slideDown
		});	

		// Register for updates. Bind the callback to this object
		var obj = this;
		CentralSplashUpdater.register( ref, HSUpdateHandler, function() { obj.draw() } );
	}
}

// ----------------------- Humidity Device Object ------------------------------------------
// Represents a Splash Humidity device

function SplashHumidDevice ( ref ) {
    this.hsdev = HSDeviceFactory.create( ref );
    // Element tot attach it to
    this.bindingElement = null;
}

SplashHumidDevice.prototype.getHSDev = function( ) {
	return this.hsdev;
}
SplashHumidDevice.prototype.setBindingElement = function( bindingElement ) {
	this.bindingElement = bindingElement;
}
SplashHumidDevice.prototype.getBindingElement = function( ) {
	return this.bindingElement;
}

SplashHumidDevice.prototype.draw = function( ) {
	console.log( timestamp() + " SplashHumidDevice.draw()");
	var hsDev = this.getHSDev();
	var ref = hsDev.getRef();
	// Does the element exist? No: draw, Yes: update
	if ( $('div#shd_' + ref).length ) {
		console.log( timestamp() + " SplashHumidDevice.draw() - Update the element");

		if ( $('h3#shd_' + ref + '_status .counter').text() != hsDev.getValue() ) {
			$('h3#shd_' + ref + '_status').html( '<b class="counter">'+hsDev.getValue()+'</b>%' );
			if (hsDev.getValue() > 0) {
		        $('h3#shd_' + ref + '_status .counter').counterUp({
		            delay: 100,
		            time: 1200
		        });
			}
		}

		$('h7#shd_' + ref + '_name').text( hsDev.getName() );
		$('p#shd_' + ref + '_location').text( hsDev.getLocation() );


	} else {
		// Element dows not exist, draw it
		console.log( timestamp() + " SplashHumidDevice.draw() - Drawing new element");
		$( this.getBindingElement() ).append('<div class="col-lg-3 col-md-6" id="shd_'+ref+'"><div class="widget-bg-color-icon card-box"><div class="bg-icon bg-icon-primary pull-left"><i class="wi wi-humidity text-primary"></i></div><div class="text-right"><h3 id="shd_'+ref+'_status" class="text-primary m-t-10">--%</h3><h7 id="shd_'+ref+'_name" class="text-dark m-t-10">--</h7><p id="shd_'+ref+'_location" class="text-muted mb-0 blockquote-reverse">--</p><div class="clearfix"></div></div></div>');

		// Onclick toggle the uptime
		$('p#shd_' + ref + '_location').slideUp();	// default slideup
		$('div#shd_'+ref).click( function(e) {
			$('p#shd_' + ref + '_location').slideToggle();	// slideUp/ slideDown
		});	

		// Register for updates. Bind the callback to this object
		var obj = this;
		CentralSplashUpdater.register( ref, HSUpdateHandler, function() { obj.draw() } );
	}
}

// ----------------------- Uptime Device Object ------------------------------------------
// Represents a Splash Uptime device

function SplashUptimeDevice ( ref ) {
    this.hsdev = HSDeviceFactory.create( ref );
    // Element tot attach it to
    this.bindingElement = null;
}

SplashUptimeDevice.prototype.getHSDev = function( ) {
	return this.hsdev;
}
SplashUptimeDevice.prototype.setBindingElement = function( bindingElement ) {
	this.bindingElement = bindingElement;
}
SplashUptimeDevice.prototype.getBindingElement = function( ) {
	return this.bindingElement;
}


SplashUptimeDevice.prototype.draw = function( ) {
	console.log( timestamp() + " SplashUptimeDevice.draw()");
	var hsDev = this.getHSDev();
	var ref = hsDev.getRef();
	// Does the element exist? No: draw, Yes: update
	if ( $('div#sud_' + ref).length ) {
		console.log( timestamp() + " SplashUptimeDevice.draw() - Update the element");

		if ( hsDev.isOff() ) {
        	// Off
        	var el = $('div#sud_'+ref+' div div.bg-icon-success');
        	el.removeClass('bg-icon-success');
        	el.addClass('bg-icon-danger');
        	el = el.find('i.mdi-laptop-mac');
        	el.removeClass('mdi-laptop-mac');
        	el.removeClass('text-success');
        	el.addClass('mdi-alert-outline');
        	el.addClass('text-pink');
        } else {
        	// On
        	var el = $('div#sud_'+ref+' div div.bg-icon-danger');
        	el.removeClass('bg-icon-danger');
        	el.addClass('bg-icon-success');
        	el = el.find('i.mdi-alert-outline');
        	el.removeClass('mdi-alert-outline');
        	el.removeClass('text-pink');
        	el.addClass('mdi-laptop-mac');
        	el.addClass('text-success');
        }

		$('h3#sud_' + ref + '_status').text( (hsDev.isOff()?'OFFLINE':'ONLINE') );
		$('h7#sud_' + ref + '_name').text( hsDev.getName() );
		$('p#sud_' + ref + '_uptime').text( hsDev.getStatus() );
		$('p#sud_' + ref + '_location').text( hsDev.getLocation() );

	} else {
		// Element dows not exist, draw it
		console.log( timestamp() + " SplashUptimeDevice.draw() - Drawing new element");
		$( this.getBindingElement() ).append('<div class="col-lg-3 col-md-6" id="sud_'+ref+'"><div class="widget-bg-color-icon card-box"><div class="bg-icon '+(hsDev.isOff()?'bg-icon-danger':'bg-icon-success')+' pull-left"><i class="mdi '+(hsDev.isOff()?'mdi-alert-outline text-pink':'mdi-laptop-mac text-success')+'"></i></div><div class="text-right"><h3 id="sud_'+ref+'_status" class="text-success m-t-10">'+(hsDev.isOff()?'OFFLINE':'ONLINE')+'</h3><h7  id="sud_'+ref+'_name" class="text-dark m-t-10">--</h7><p id="sud_'+ref+'_location" class="text-muted mb-0 blockquote-reverse">--</p><p id="sud_'+ref+'_uptime" class="text-muted mb-0 blockquote-reverse" style="margin-top: 30px;">--</p><div class="clearfix"></div></div></div>');

		// Onclick toggle the uptime
		$('p#sud_' + ref + '_uptime').slideUp();	// default slideup
		$('p#sud_' + ref + '_location').slideUp();	// default slideup
		$('div#sud_'+ref).click( function(e) {
			$('p#sud_' + ref + '_uptime').slideToggle();	// slideUp/ slideDown
			$('p#sud_' + ref + '_location').slideToggle();	// slideUp/ slideDown
			$('p#sud_' + ref + '_location2').slideToggle();	// slideUp/ slideDown
		});	

		// Register for updates. Bind the callback to this object
		var obj = this;
		CentralSplashUpdater.register( ref, HSUpdateHandler, function() { obj.draw() } );
	}
}


// ----------------------- Two Button Fan Device Object ------------------------------------------
// Represents a Splash Fan device controlled by 2 switches 

function SplashTwoButtonFanDevice ( name, refLow, refHigh ) {
    this.name = name;
    this.hsDevLow = HSDeviceFactory.create( refLow );
    this.hsDevHigh = HSDeviceFactory.create( refHigh );
    // Element tot attach it to
    this.bindingElement = null;
}

SplashTwoButtonFanDevice.prototype.getName = function( ) {
	return this.name;
}
SplashTwoButtonFanDevice.prototype.setName = function( name ) {
	this.name = name;
}
SplashTwoButtonFanDevice.prototype.getHSDevLow = function( ) {
	return this.hsDevLow;
}
SplashTwoButtonFanDevice.prototype.getHSDevHigh = function( ) {
	return this.hsDevHigh;
}
SplashTwoButtonFanDevice.prototype.setBindingElement = function( bindingElement ) {
	this.bindingElement = bindingElement;
}
SplashTwoButtonFanDevice.prototype.getBindingElement = function( ) {
	return this.bindingElement;
}
SplashTwoButtonFanDevice.prototype.draw = function( ) {
	console.log( timestamp() + " SplashTwoButtonFanDevice.draw()");
	this.drawElement( );
	this.drawSlider();
	this.drawButtons();
}

SplashTwoButtonFanDevice.prototype.drawElement = function( ) {
	console.log( timestamp() + " SplashTwoButtonFanDevice.drawElement()");
	var hsDevLow = this.getHSDevLow();
	var hsDevHigh = this.getHSDevHigh();
	var refLow = hsDevLow.getRef();
	var refHigh = hsDevHigh.getRef();
	// Does the element exist? No: draw, Yes: update
	if ( $('div#stbfd_' + refLow + refHigh).length ) {

		// If on
		if ( hsDevLow.getValue() > 0 || hsDevHigh.getValue() > 0 ) {
			// Definately on
			$('#stbfd_' + refLow + refHigh + '_bg-icon').addClass('bg-icon-warning');
			$('#stbfd_' + refLow + refHigh + '_bg-icon').removeClass('bg-icon-primary');
			$('#stbfd_' + refLow + refHigh + '_spin').addClass('fa-rotate-right');
			$('#stbfd_' + refLow + refHigh + '_spin').removeClass('fa-hand-stop-o');
			$('#stbfd_' + refLow + refHigh + '_spin').addClass('fa-spin');
		} else {
			// Off
			$('#stbfd_' + refLow + refHigh + '_bg-icon').addClass('bg-icon-primary');
			$('#stbfd_' + refLow + refHigh + '_bg-icon').removeClass('bg-icon-warning');			
			$('#stbfd_' + refLow + refHigh + '_spin').addClass('fa-hand-stop-o');
			$('#stbfd_' + refLow + refHigh + '_spin').removeClass('fa-rotate-right');
			$('#stbfd_' + refLow + refHigh + '_spin').removeClass('fa-spin');
		}
		switch ( Math.min(hsDevLow.getValue(), 1) + (Math.min(hsDevHigh.getValue(), 1) * 2) ) {
			case 3:
				$('#stbfd_' + refLow + refHigh + '_status').text( 'Hoog' );				
				break;
			case 2:
				$('#stbfd_' + refLow + refHigh + '_status').text( 'Midden' );				
				break;
			case 1:
				$('#stbfd_' + refLow + refHigh + '_status').text( 'Laag' );				
				break;
			case 0:
			default:
				$('#stbfd_' + refLow + refHigh + '_status').text( 'UIT' );				
		}
		$('#stbfd_' + refLow + refHigh + '_name').text( this.getName() );
		$('#stbfd_' + refLow + refHigh + '_location').text( hsDevLow.getLocation() );
		
	} else {
		// Element does not exist, draw it
		console.log( timestamp() + " SplashTwoButtonFanDevice.drawElement() - Drawing new element");
        $( this.getBindingElement() ).append('<div class="col-lg-3 col-md-6" id="stbfd_' + refLow + refHigh + '"><div class="widget-bg-color-icon card-box"><div id="stbfd_' + refLow + refHigh + '_bg-icon" class="bg-icon bg-icon-primary pull-left"><i id="stbfd_' + refLow + refHigh + '_spin" class="fa fa-hand-stop-o text-primary"></i></div><div id="stbfd_' + refLow + refHigh + '_textbox" class="wid-icon-info text-right"><div class="text-right"><h3 id="stbfd_' + refLow + refHigh + '_status" class="text-primary m-t-10">--</h3><h7 id="stbfd_' + refLow + refHigh + '_name" class="text-dark m-t-10">--</h7><p id="stbfd_' + refLow + refHigh + '_location" class="text-muted mb-0 blockquote-reverse">--</p></div><div class="clearfix"></div></div></div>');

		// onclick toggle the location
		$('#stbfd_' + refLow + refHigh + '_location').slideToggle();	// default slideup
		$('#stbfd_' + refLow + refHigh).click( function(e) {
				$('#stbfd_' + refLow + refHigh + '_location').slideToggle();	// slideUp/ slideDown
		});

		// Register for updates. Bind the callback to this object
		var obj = this;
		CentralSplashUpdater.register( refLow, HSUpdateHandler, function() { obj.draw() } );
		CentralSplashUpdater.register( refHigh, HSUpdateHandler, function() { obj.draw() } );
	}
}

SplashTwoButtonFanDevice.prototype.drawSlider = function( ) {
	var hsDevLow = this.getHSDevLow();
	var hsDevHigh = this.getHSDevHigh();
	var refLow = hsDevLow.getRef();
	var refHigh = hsDevHigh.getRef();
	// Does the slider exist? No: draw, Yes: update
	if ( $('div#stbfd_sliderblock_' + refLow + refHigh).length ) {
		// Slider exists, update it
		console.log( timestamp() + " SplashTwoButtonFanDevice.drawSlider() - Updating existing slider");
				
		// Update the slider, and potentially enable it, if this is the first update
    	var $range = $("#stbfd_slider_" +  refLow + refHigh );
    	var slider = $range.data("ionRangeSlider");
		// Is it different?
		console.log( timestamp() + " SplashTwoButtonFanDevice.drawSlider() - slider.result.from: " + slider.result.from + " hsDevLow.getValue(): " + hsDevLow.getValue() + " hsDevHigh.getValue(): " + hsDevHigh.getValue() );
		if ( slider.result.from != ( Math.min(hsDevLow.getValue(), 1) + (Math.min(hsDevHigh.getValue(), 1) * 2) ) ) {
			console.log( timestamp() + " SplashTwoButtonFanDevice.drawSlider() - updating actual slider" );
	        slider.update({
	            from: ( Math.min(hsDevLow.getValue(), 1) + (Math.min(hsDevHigh.getValue(), 1) * 2) ),
		        disable: false
	        });
		};
	} else {
		// Slider does not exist, draw it
		console.log( timestamp() + " SplashTwoButtonFanDevice.drawSlider() - Drawing new slider");
        $( 'div#stbfd_'+ refLow + refHigh +'_textbox' ).append('<div id="stbfd_sliderblock_' + refLow + refHigh + '"><input type="text" id="stbfd_slider_' + refLow + refHigh + '"></div>');

		// Initialise the slider
		console.log( timestamp() + ' Initialise the slider [' + refLow + ' ' + refHigh + '] in SplashTwoButtonFanDevice.drawSlider()' );

		// Dimmer, onclick toggle the slider
		$('div#stbfd_sliderblock_' + refLow + refHigh).slideToggle();	// default slideup
		$('div#stbfd_' + refLow + refHigh).click( function(e) {
				$('div#stbfd_sliderblock_' + refLow + refHigh).slideToggle();	// slideUp/ slideDown
		});	// Stop slideup by clicking on the slider
		$('div#stbfd_sliderblock_' + refLow + refHigh).click(function(event){
			event.stopPropagation();
		});

		var $range = $("#stbfd_slider_" + refLow + refHigh );          
	    $range.ionRangeSlider({
	        type: "single",
			grid: true,
	        min: 0,
	        max: 3,
			values: [ "UIT", "Laag", "Midden", "Hoog" ],
	        hide_min_max: true,
	        hide_from_to: false,
	        from: 0,
	        grid_snap: true,
	        disable: false,
	        keyboard: true,
	        onStart: function (data) {
				console.log( timestamp() + ' ---> Slider ' + refLow + ' ' + refHigh + ' started');
	        },
	        onChange: function (data) {
				console.log( timestamp() + ' ---> Slider ' + refLow + ' ' + refHigh + ' changed to ' + data.from);
				ThrottleSplashHSDeviceUpdate( refLow, ( data.from == 1 || data.from == 3 ? 255 : 0 ) );
				ThrottleSplashHSDeviceUpdate( refHigh, ( data.from == 2 || data.from == 3 ? 255 : 0 ) );
	        },
	        onFinish: function (data) {
	        	console.log( timestamp() + ' ---> Slider ' + refLow + ' ' + refHigh + ' finished on ' + data.from);
				// update the device now, don't way for the device to get the update itself
				var hsDevLow = HSDeviceFactory.create( refLow );
				var hsDevHigh = HSDeviceFactory.create( refHigh );
				hsDevLow.setValue( ( data.from == 1 || data.from == 3 ? 255 : 0 ) );			
				hsDevHigh.setValue( ( data.from == 2 || data.from == 3 ? 255 : 0 ) );			
				// Now notify the callbacks
// TODO - deze zingt rond als je naast de slider klikt? ( dus niet drag, maar ernaast klikken)
				CentralSplashUpdater.notify( HSUpdateHandler.uidt, hsDevLow );
				CentralSplashUpdater.notify( HSUpdateHandler.uidt, hsDevHigh );				
	        },
	        onUpdate: function (data) {
				console.log( timestamp() + ' ---> Slider ' + refLow + ' ' + refHigh + ' updated');
	        }
	    });

		// No need to register for updates. Draw will be called for this object
	}
}

SplashTwoButtonFanDevice.prototype.drawButtons = function( ) {
	var hsDevLow = this.getHSDevLow();
	var hsDevHigh = this.getHSDevHigh();
	var refLow = hsDevLow.getRef();
	var refHigh = hsDevHigh.getRef();
	// Do the buttons exist? No: draw, Yes: ignore
	if ( ! $('div#stbfd_buttonblock_' + refLow + refHigh).length ) {
		// Buttons do not exist, draw them

		console.log( timestamp() + " SplashTwoButtonFanDevice.draw() - Drawing buttons");
		$( 'div#stbfd_'+ refLow + refHigh +'_textbox' ).append('<div id="stbfd_buttonblock_' + refLow + refHigh + '" class="stbfd_activity_wrapper"><div class="btn-group m-b-10"><button type="button" id="stbfd_' + refLow + refHigh + '_off" class="btn btn-light waves-effect"> <i class="fa fa-toggle-off m-r-5"></i> </button><button type="button" id="stbfd_' + refLow + refHigh + '_low" class="btn btn-outline-success waves-effect waves-dark"> <span>Laag</span></button><button type="button" id="stbfd_' + refLow + refHigh + '_medium" class="btn btn-outline-warning waves-effect waves-light"> <span>Midden</span> </button><button type="button" id="stbfd_' + refLow + refHigh + '_high" class="btn btn-outline-danger waves-effect waves-light"> <span>Hoog</span> </button></div>');
		
//		btn-outline-info 
//		btn-outline-success  btn-outline-warning 
//		btn-outline-danger 
		
	
		// onclick toggle the buttons
		$('div#stbfd_buttonblock_' + refLow + refHigh ).slideToggle();	// default slideup
		$('div#stbfd_' + refLow + refHigh).click( function(e) {
			$('div#stbfd_buttonblock_' + refLow + refHigh ).slideToggle();	// slideUp/ slideDown
		});	// Stop slideup by clicking on the button
		$('div#stbfd_buttonblock_' + refLow + refHigh ).click(function(event){
			event.stopPropagation();
		});

		var slrdObj = this;
		$('button#stbfd_' + refLow + refHigh + '_off').on("click", function () {
			hsDevLow.setValue( 0 );
			hsDevHigh.setValue( 0 );
			ThrottleSplashHSDeviceUpdate( refLow, 0 );
			ThrottleSplashHSDeviceUpdate( refHigh, 0 );
		});
		$('button#stbfd_' + refLow + refHigh + '_low').on("click", function () {
			hsDevLow.setValue( 255 );
			hsDevHigh.setValue( 0 );
			ThrottleSplashHSDeviceUpdate( refLow, 255 );
			ThrottleSplashHSDeviceUpdate( refHigh, 0 );
		});
		$('button#stbfd_' + refLow + refHigh + '_medium').on("click", function () {
			hsDevLow.setValue( 0 );
			hsDevHigh.setValue( 255 );
			ThrottleSplashHSDeviceUpdate( refLow, 0 );
			ThrottleSplashHSDeviceUpdate( refHigh, 255 );
		});
		$('button#stbfd_' + refLow + refHigh + '_high').on("click", function () {
			hsDevLow.setValue( 255 );
			hsDevHigh.setValue( 255 );
			ThrottleSplashHSDeviceUpdate( refLow, 255 );
			ThrottleSplashHSDeviceUpdate( refHigh, 255 );
		});
		// No need to register for updates. Draw will be called for this object
	}
}
// ----------------------- Light Device Object ------------------------------------------
// Represents a Splash Light device

function SplashLightDevice ( ref ) {
    this.hsdev = HSDeviceFactory.create( ref );
    // Element tot attach it to
    this.bindingElement = null;
    this.circleColor = CIRCLIFUL_COLOR_BLUE;
    this.dataColor = CIRCLIFUL_COLOR_BG;
	// Default width class. Works with col-lg-4, col-lg-6 and col-12
    this.widthClass = 'col-lg-3';	// col-lg-3 col-md-6
}
SplashLightDevice.prototype.getHSDev = function( ) {
	return this.hsdev;
}
SplashLightDevice.prototype.setBindingElement = function( bindingElement ) {
	this.bindingElement = bindingElement;
}
SplashLightDevice.prototype.getBindingElement = function( ) {
	return this.bindingElement;
}
SplashLightDevice.prototype.getCircleColor = function( ) {
	return this.circleColor;
}
SplashLightDevice.prototype.setCircleColor = function( circleColor ) {
	this.circleColor = circleColor;
}
SplashLightDevice.prototype.getDataColor = function( ) {
	return this.dataColor;
}
SplashLightDevice.prototype.setDataColor = function( dataColor ) {
	this.dataColor = dataColor;
}
SplashLightDevice.prototype.setWidthClass = function( widthClass ) {
	this.widthClass = widthClass;
}
SplashLightDevice.prototype.getWidthClass = function( ) {
	return this.widthClass;
}

// Returns boolean true/false
/* Handles typical HomeSeer last changed date strings like /Date(1517243403149)/ */
SplashLightDevice.prototype.hasChangedInLastXDays = function( days ) {
    
    var lastChangeDate = this.getHSDev().getLastChange();	
    if ( lastChangeVal == null || !(lastChangeDate instanceof Date) ) {
    	return false;
    }
	// parse
	var dateOffset = (24*60*60*1000) * days;
	var timeWarning = ( ( new Date().getTime() - dateOffset ) > lastChangeDate.getTime() );
    return timeWarning;
};

SplashLightDevice.prototype.draw = function( ) {
	console.log( timestamp() + " SplashLightDevice.draw()");
	this.drawElement( );
	console.log( timestamp() + " SplashLightDevice.draw() - canDim: " + this.getHSDev().canDim() );
	if ( this.getHSDev().canDim() ) {
		console.log( timestamp() + " SplashLightDevice.draw() - canDim, drawing slider");
		this.drawSlider();
	}	
	if ( this.getHSDev().isSwitch() ) {
		this.drawOnOffButtons( );
	}
}

SplashLightDevice.prototype.drawElement = function( ) {
	console.log( timestamp() + " SplashLightDevice.drawElement()");
	var hsDev = this.getHSDev();
	var ref = hsDev.getRef();
	// Does the element exist? No: draw, Yes: update
	if ( $('div#sld_' + ref).length ) {

		// Element exist, do we need to change from light to dimmer?
		if ( hsDev.canDim() && $('div#sld_' + ref).find('div.widget-bg-color-icon').length ) {
			// The icon exists, the dimmer is requested
			console.log( timestamp() + " SplashLightDevice.drawElement() - replace light with dimmer");
			$('div#sld_' + ref + ' div:nth-child(1)').removeClass('widget-bg-color-icon');
			$('div#sld_' + ref + ' div:nth-child(1)').addClass('widget-simple-chart');
			$('div#sld_' + ref + ' div:nth-child(1)').addClass('text-right');
			$('div#sld_' + ref + ' div:nth-child(1)  div:nth-child(1)').remove();
			$('div#sld_' + ref + ' div:nth-child(1)').prepend('<div id="sld_'+ref+'_circliful" class="circliful-chart" data-dimension="90" data-text="'+hsDev.getValue()+'%" data-width="5" data-fontsize="14" data-percent="'+hsDev.getValue()+'" data-fgcolor="'+this.getCircleColor()+'" data-bgcolor="'+this.getDataColor()+'"></div>');
			$('#sld_'+ref+'_circliful').circliful();
		} else if ( hsDev.canDim() && $('div#sld_'+ref+' div.circliful-chart').attr('data-percent') != hsDev.getValue() ) {
			// It is different, update it
			console.log( timestamp() + " SplashLightDevice.drawElement() - Updating existing Dimmer element");
			$('#sld_' + ref + '_circliful').empty().removeData().attr('data-percent', hsDev.getValue()).attr('data-text', hsDev.getValue()+'%').attr('data-fgcolor', this.getCircleColor()).attr('data-bgcolor', this.getDataColor()).circliful();
		} if ( hsDev.isSwitch() ) {
			// Switch - where is the On/Off value?
            $('#sld_'+ref+'_circle').toggleClass( 'bg-icon-warning', ( !hsDev.isOff() ) );
            $('#sld_'+ref+'_circle').toggleClass( 'bg-icon-inverse', hsDev.isOff() );
            
        	$('#sld_'+ref+'_bulbicon').toggleClass( 'ion-ios7-lightbulb-outline', hsDev.isOff() );
        	$('#sld_'+ref+'_bulbicon').toggleClass( 'ion-ios7-lightbulb', ( !hsDev.isOff() ) );
        	// Check the switch
        	$('input#sld_'+ref+'_onoff').prop('checked', ( !hsDev.isOff() ) );
		}
		
		$('p#sld_' + ref + '_name').text( hsDev.getName() );
		$('p#sld_' + ref + '_func').text( hsDev.getTypeStr() );		
		$('span#sld_' + ref + '_location').text( hsDev.getLocation() );
	} else {
		// Element does not exist, draw it
		console.log( timestamp() + " SplashLightDevice.drawElement() - Drawing new element");
		if ( hsDev.canDim() ) {
			// Draw dimmer
			console.log( timestamp() + " SplashLightDevice.drawElement() - Drawing new Dimmer element");

	        var elStr = `<div class="TOKEN_WIDTH_CLASS" id="sld_TOKEN_REF'">
	        	<div class="widget-simple-chart text-right card-box">
	        		<div id="sld_TOKEN_REF_circliful" class="circliful-chart" data-dimension="90" data-text="--%" data-width="5" data-fontsize="14" data-percent="100" data-fgcolor="CIRCLIFUL_COLOR_GRAY" data-bgcolor="CIRCLIFUL_COLOR_BG_GRAY"></div>
	        		<div id="sld_TOKEN_REF_textbox" class="wid-icon-info text-right">
	        			<p id="sld_TOKEN_REF_name" class="text-muted m-b-5 font-13 text-uppercase">---</p>
	        			<p id="sld_TOKEN_REF_func" class="text-muted m-b-5 font-15">---</p>
	        			<h5 class="m-t-0 m-b-5 font-bold">
	        				<span id="sld_TOKEN_REF_location">---</span>
	        			</h5>
	        		</div>
	        	</div>
	        </div>`;

			elStr = elStr.replace( /TOKEN_REF/g, ref );
			elStr = elStr.replace( /TOKEN_WIDTH_CLASS/g, this.getWidthClass() );
			elStr = elStr.replace( /CIRCLIFUL_COLOR_GRAY/g, CIRCLIFUL_COLOR_GRAY );
			elStr = elStr.replace( /CIRCLIFUL_COLOR_BG_GRAY/g, CIRCLIFUL_COLOR_BG_GRAY );

	        $( this.getBindingElement() ).append( elStr );

		} else {
			// Draw regular light
			console.log( timestamp() + " SplashLightDevice.drawElement() - Drawing new Switch element");

	        var elStr = `<div class="TOKEN_WIDTH_CLASS" id="sld_TOKEN_REF">
	        	<div class="widget-bg-color-icon card-box">
	        		<div id="sld_TOKEN_REF_circle" class="bg-icon bg-icon-inverse pull-left">
	        			<i id="sld_TOKEN_REF_bulbicon" class="ion-ios7-lightbulb-outline text-purple"></i>
	        		</div>
	        		<div id="sld_TOKEN_REF_textbox" class="wid-icon-info text-right">
	        			<p id="sld_TOKEN_REF_name" class="text-muted m-b-5 font-13 text-uppercase">---</p>
	        			<p id="sld_TOKEN_REF_func" class="text-muted m-b-5 font-15">---</p>
	        			<h5 class="m-t-0 m-b-5 font-bold">
	        				<span id="sld_TOKEN_REF_location">---</span>
	        			</h5>
	        		</div>
	        	</div>
	        </div>`;

			elStr = elStr.replace( /TOKEN_REF/g, ref );
			elStr = elStr.replace( /TOKEN_WIDTH_CLASS/g, this.getWidthClass() );

	        $( this.getBindingElement() ).append( elStr );

		}
		// Register for updates. Bind the callback to this object
		var obj = this;
		CentralSplashUpdater.register( ref, HSUpdateHandler, function() { obj.draw() } );
	}
}

SplashLightDevice.prototype.drawSlider = function( ) {
	var hsDev = this.getHSDev();
	var ref = hsDev.getRef();
	// Does the slider exist? No: draw, Yes: update
	if ( $('div#sld_sliderblock_' + ref).length ) {
		// Slider exists, update it
		console.log( timestamp() + " SplashLightDevice.drawSlider() - Updating existing slider");
				
		// Update the slider, and potentially enable it, if this is the first update
    	var $range = $("#sld_slider_" + ref );
    	var slider = $range.data("ionRangeSlider");
		// Is it different?
		console.log( timestamp() + " SplashLightDevice.drawSlider() - slider.result.from: " + slider.result.from + " hsDev.getValue(): " + hsDev.getValue() );
		if ( slider.result.from != hsDev.getValue() ) {
			console.log( timestamp() + " SplashLightDevice.drawSlider() - updating actual slider" );
	        slider.update({
	            from: Math.min(hsDev.getValue(), 100),
		        disable: false
	        });
		};
	} else {
		// Slider does not exist, draw it
		console.log( timestamp() + " SplashLightDevice.drawSlider() - Drawing new slider");
        $( 'div#sld_'+ref+' div.card-box' ).append('<div id="sld_sliderblock_' + ref + '"><input type="text" id="sld_slider_' + ref + '"></div>');

		// Initialise the slider
		console.log( timestamp() + ' Initialise the slider [' + ref + '] in SplashLightDevice.drawSlider()' );

		// Dimmer, onclick toggle the slider
		$('div#sld_sliderblock_' + ref).slideToggle();	// default slideup
		$('div#sld_'+ref).click( function(e) {
				$('div#sld_sliderblock_' + ref).slideToggle();	// slideUp/ slideDown
		});	// Stop slideup by clicking on the slider
		$('div#sld_sliderblock_' + ref).click(function(event){
			event.stopPropagation();
		});

		var $range = $("#sld_slider_" + ref );          
	    $range.ionRangeSlider({
	        type: "single",
			grid: true,
	        min: 0,
	        max: 100,
	        hide_min_max: true,
	        hide_from_to: false,
	        from: hsDev.getValue(),
	        disable: false,
	        keyboard: true,
	        onStart: function (data) {
				console.log( timestamp() + ' ---> Slider ' + ref + ' started');
	        },
	        onChange: function (data) {
				console.log( timestamp() + ' ---> Slider ' + ref + ' changed to ' + data.from);
				ThrottleSplashHSDeviceUpdate( ref, data.from );
	        },
	        onFinish: function (data) {
	        	console.log( timestamp() + ' ---> Slider ' + ref + ' finished on ' + data.from);
				// update the device now, don't way for the device to get the update itself
				var hsDev = HSDeviceFactory.create( ref );
				hsDev.setValue( data.from );			
				// Now notify the callbacks
// TODO - deze zingt rond als je naast de slider klikt? ( dus niet drag, maar ernaast klikken)
				CentralSplashUpdater.notify( HSUpdateHandler.uidt, hsDev );
	        },
	        onUpdate: function (data) {
				console.log( timestamp() + ' ---> Slider ' + ref + ' updated');
	        }
	    });

		// No need to register for updates. Draw will be called for this object
	}
}

SplashLightDevice.prototype.drawOnOffButtons = function( ) {
	var hsDev = this.getHSDev();
	var ref = hsDev.getRef();
	// Do the buttons exist? No: draw, Yes: ignore
	if ( ! $('div#sld_buttonblock_' + ref).length ) {
		// Buttons do not exist, draw them
		console.log( timestamp() + " SplashLightDevice.drawOnOffButtons() - Drawing buttons");
		$( 'div#sld_'+ref+' div.card-box' ).append('<div id="sld_buttonblock_' + ref + '" class="sld_onoff_wrapper"><div class="onoffswitch"><input type="checkbox" name="onoffswitch" class="onoffswitch-checkbox" id="sld_'+ref+'_onoff"'+(hsDev.getValue()!=0?' checked':'')+'><label class="onoffswitch-label" for="sld_'+ref+'_onoff"><span class="onoffswitch-inner"></span><span class="onoffswitch-switch"></span></label></div></div>');
		// Initialise the buttons
		console.log( timestamp() + ' Initialise the buttons [' + ref + '] in SplashLightDevice.drawOnOffButtons()' );

		// Dimmer, onclick toggle the buttons
		$('div#sld_buttonblock_' + ref).slideToggle();	// default slideup
		$('div#sld_'+ref).click( function(e) {
				$('div#sld_buttonblock_' + ref).slideToggle();	// slideUp/ slideDown
		});	// Stop slideup by clicking on the button
		$('div#sld_buttonblock_' + ref).click(function(event){
			event.stopPropagation();
		});

		$('input#sld_'+ref+'_onoff').on('click', function() {			
			console.log('Clicked...');
			
			// Switch - where is the On/Off value?
            $('#sld_'+ref+'_circle').toggleClass( 'bg-icon-warning', $(this).is(":checked") );
            $('#sld_'+ref+'_circle').toggleClass( 'bg-icon-inverse', ( !$(this).is(":checked") ) );
            
        	$('#sld_'+ref+'_bulbicon').toggleClass( 'ion-ios7-lightbulb-outline', ( !$(this).is(":checked") ) );
        	$('#sld_'+ref+'_bulbicon').toggleClass( 'ion-ios7-lightbulb', $(this).is(":checked") );

			hsDev.setValue( ($(this).is(":checked")?255:0) );
			ThrottleSplashHSDeviceUpdate( ref, hsDev.getValue() );
        });

		// No need to register for updates. Draw will be called for this object
	}
}

SplashLightDevice.prototype.drawDimmerElement = function( ) {
	var hsDev = this.getHSDev();
	var ref = hsDev.getRef();
	// Does the element exist? No: draw, Yes: update
	if ( $('div#sld_' + ref).length ) {
		// Element exist, update it
		console.log( timestamp() + " SplashLightDevice.drawDimmerElement() - Updating existing element");
		// Is it different?
		if ( $('div#sld_'+ref+' div.circliful-chart').attr('data-percent') != hsDev.getValue() ) {
		// New value, update it
			$('div#sld_'+ref+' div.circliful-chart').empty().removeData().attr('data-percent', hsDev.getValue()).attr('data-text', hsDev.getValue()+'%').attr('data-fgcolor', this.getCircleColor()).attr('data-bgcolor', this.getDataColor()).circliful()
		}
		$('p#sld_' + ref + '_name').text( hsDev.getName() );
		$('p#sld_' + ref + '_func').text( 'Dimmer' );		
		$('span#sld_' + ref + '_location').text( hsDev.getLocation() );
		// Update the slider, and potentially enable it, if this is the first update
    	var $range = $("#sld_slider_" + ref );
    	var slider = $range.data("ionRangeSlider");
        slider.update({
            from: Math.min(hsDev.getValue(), 100),
	        disable: false
        });
	} else {
		// Element dows not exist, draw it
		console.log( timestamp() + " SplashLightDevice.drawDimmerElement() - Drawing new element");
        $( this.getBindingElement() ).append('<div class="col-lg-3 col-md-6" id="sld_'+ref+'"><div class="widget-simple-chart text-right card-box"><div class="circliful-chart" data-dimension="90" data-text="--%" data-width="5" data-fontsize="14" data-percent="100" data-fgcolor="'+CIRCLIFUL_COLOR_GRAY+'" data-bgcolor="'+CIRCLIFUL_COLOR_BG_GRAY+'"></div><div class="wid-icon-info text-right"><p id="sld_'+ref+'_name" class="text-muted m-b-5 font-13 text-uppercase">---</p><p id="sld_'+ref+'_func" class="text-muted m-b-5 font-15">---</p><h5 class="m-t-0 m-b-5 font-bold"><span id="sld_'+ref+'_location">---</span></h5> <div id="sld_sliderblock_' + ref + '"><input type="text" id="sld_slider_' + ref + '"></div> </div></div></div>');

		// Initialise the slider
		console.log( timestamp() + ' Initialise the slider [' + ref + '] in SplashLightDevice.drawDimmerElement()' );

		// Dimmer, onclick toggle the slider
		$('div#sld_sliderblock_' + ref).slideToggle();	// default slideup
		$('div#sld_'+ref).click( function(e) {
				$('div#sld_sliderblock_' + ref).slideToggle();	// slideUp/ slideDown
		});	// Stop slideup by clicking on the slider
		$('div#sld_sliderblock_' + ref).click(function(event){
			event.stopPropagation();
		});

		var $range = $("#sld_slider_" + ref );          
	    $range.ionRangeSlider({
	        type: "single",
			grid: true,
	        min: 0,
	        max: 100,
	        hide_min_max: true,
	        hide_from_to: false,
	        from: 50,
	        disable: false,
	        keyboard: true,
	        onStart: function (data) {
				console.log( timestamp() + ' ---> Slider ' + ref + ' started');
	        },
	        onChange: function (data) {
				console.log( timestamp() + ' ---> Slider ' + ref + ' changed to ' + data.from);
				hsDev.setValue( data.from );
				ThrottleSplashHSDeviceUpdate( ref, data.from );
	        },
	        onFinish: function (data) {
	        	console.log( timestamp() + ' ---> Slider ' + ref + ' finished on ' + data.from);
				// update the device now, don't way for the device to get the update itself
//				var hsDev = HSDeviceFactory.create( ref );
				hsDev.setValue( data.from );			
				// Now notify the callbacks
				CentralSplashUpdater.notify( HSUpdateHandler.uidt, hsDev );
	        },
	        onUpdate: function (data) {
				console.log( timestamp() + ' ---> Slider ' + ref + ' updated');
	        }
	    });

		// Register for updates. Bind the callback to this object
		var obj = this;
		CentralSplashUpdater.register( ref, HSUpdateHandler, function() { obj.draw() } );
	}
}


// ----------------------- FAN Device Object ------------------------------------------
// Represents a Splash FAN device

function SplashOneButtonFanDevice ( ref ) {
    this.hsdev = HSDeviceFactory.create( ref );
    // Element tot attach it to
    this.bindingElement = null;
}

SplashOneButtonFanDevice.prototype.getHSDev = function( ) {
	return this.hsdev;
}
SplashOneButtonFanDevice.prototype.setBindingElement = function( bindingElement ) {
	this.bindingElement = bindingElement;
}
SplashOneButtonFanDevice.prototype.getBindingElement = function( ) {
	return this.bindingElement;
}

SplashOneButtonFanDevice.prototype.draw = function( ) {
	console.log( timestamp() + " SplashFANDevice.draw()");
	var hsDev = this.getHSDev();
	var ref = hsDev.getRef();
	// Does the element exist? No: draw, Yes: update
	if ( $('div#sobfd_' + ref).length ) {

		// Element exist
		// If on
		if ( hsDev.getValue() > 0 ) {
			// Definately on
			$('#sobfd_' + ref + '_bg-icon').addClass('bg-icon-warning');
			$('#sobfd_' + ref + '_bg-icon').removeClass('bg-icon-primary');
			$('#sobfd_' + ref + '_spin').addClass('fa-rotate-right');
			$('#sobfd_' + ref + '_spin').removeClass('fa-hand-stop-o');
			$('#sobfd_' + ref + '_spin').addClass('fa-spin');
			$('#sobfd_' + ref + '_status').text( 'ON' );				
        	// Check the switch
        	$('input#sobfd_'+ref+'_onoff').prop('checked', true);
		} else {
			// Off
			$('#sobfd_' + ref + '_bg-icon').addClass('bg-icon-primary');
			$('#sobfd_' + ref + '_bg-icon').removeClass('bg-icon-warning');			
			$('#sobfd_' + ref + '_spin').addClass('fa-hand-stop-o');
			$('#sobfd_' + ref + '_spin').removeClass('fa-rotate-right');
			$('#sobfd_' + ref + '_spin').removeClass('fa-spin');
			$('#sobfd_' + ref + '_status').text( 'UIT' );
        	// Uncheck the switch
        	$('input#sobfd_'+ref+'_onoff').prop('checked', false);
		}
		$('#sobfd_' + ref + '_name').text( hsDev.getName() );
		$('#sobfd_' + ref + '_location').text( hsDev.getLocation() );


	} else {
		// Element does not exist, draw it
		console.log( timestamp() + " SplashFANDevice.draw() - Drawing new element");

		var elStr = `<div class="col-lg-3 col-md-6" id="sobfd_TOKEN_REF">
        	<div class="widget-bg-color-icon card-box">
        		<div id="sobfd_TOKEN_REF_bg-icon" class="bg-icon bg-icon-primary pull-left">
        			<i id="sobfd_TOKEN_REF_spin" class="fa fa-hand-stop-o text-primary"></i>
        		</div>
        		<div id="sobfd_TOKEN_REF_textbox" class="wid-icon-info text-right">
        			<div class="text-right">
        				<h3 id="sobfd_TOKEN_REF_status" class="text-primary m-t-10">--</h3>
        				<h7 id="sobfd_TOKEN_REF_name" class="text-dark m-t-10">--</h7>
        				<p id="sobfd_TOKEN_REF_location" class="text-muted mb-0 blockquote-reverse">--</p>
        			</div>
        		<div class="clearfix"></div>				
			</div>
        </div>`;

		elStr = elStr.replace( /TOKEN_REF/g, ref );					// Homeseer device ref for device
		$( this.getBindingElement() ).append( elStr );

		// Initialise the button
		console.log( timestamp() + ' Initialise the button [' + ref + '] in SplashFANDevice.draw()' );

		// Adding the button. Including this in elStr variable screws up the switch
		$( 'div#sobfd_'+ref+' div.card-box' ).append('<div id="sobfd_buttonblock_' + ref + '" class="sobfd_onoff_wrapper"><div class="onoffswitch"><input type="checkbox" name="onoffswitch" class="onoffswitch-checkbox" id="sobfd_'+ref+'_onoff"'+(hsDev.getValue()!=0?' checked':'')+'><label class="onoffswitch-label" for="sobfd_'+ref+'_onoff"><span class="onoffswitch-inner"></span><span class="onoffswitch-switch"></span></label></div></div>');

		// onclick toggle the buttons
		$('div#sobfd_buttonblock_' + ref).slideToggle();	// default slideup
		$('div#sobfd_'+ref).click( function(e) {
				$('div#sobfd_buttonblock_' + ref).slideToggle();	// slideUp/ slideDown
		});	// Stop slideup by clicking on the button
		$('div#sobfd_buttonblock_' + ref).click(function(event){
			event.stopPropagation();
		});

		$('input#sobfd_'+ref+'_onoff').on('click', function() {			
			console.log('Clicked...');
			if ( $(this).is(":checked") ) {
            	// On
				hsDev.setValue( 255 );
				// Now notify the callbacks for fast user response
				CentralSplashUpdater.notify( HSUpdateHandler.uidt, hsDev );
				ThrottleSplashHSDeviceUpdate( ref, 255 );
            } else {
            	// Off
				hsDev.setValue( 0 );
				// Now notify the callbacks for fast user response
				CentralSplashUpdater.notify( HSUpdateHandler.uidt, hsDev );
				ThrottleSplashHSDeviceUpdate( ref, 0 );
            }
        });

		// Register for updates. Bind the callback to this object
		var obj = this;
		CentralSplashUpdater.register( ref, HSUpdateHandler, function() { obj.draw() } );
	}
}



// SplashDeviceSequenceUpdate function( ref, valueArray )
//function SplashDeviceSequenceUpdate( ref, valueArray ) {
function SplashHSDeviceUpdate( ref, valueArray ) {
	var value = valueArray;
	if (Array.isArray( valueArray )) {
		value = valueArray.shift();
	}
	var jqxhr = $.getJSON( "assets/php/homeseer.controldevicebyvalue.php?ref=" + ref + "&value=" + value, function() {
		console.log( timestamp() + " SplashHSDeviceUpdate(" + ref + ", " + value + ") - Successful controldevicebyvalue jqxhr request" );
	})
	.done(function( data ) {
		console.log( timestamp() + " SplashHSDeviceUpdate(" + ref + ", " + value + ") - Successful controldevicebyvalue jqxhr response" );
		// Run the next command
	if (Array.isArray( valueArray ) && valueArray.length > 0) {
			SplashHSDeviceUpdate( ref, valueArray );
		}
	})
	.fail(function() {
		console.log( timestamp() + " SplashHSDeviceUpdate(" + ref + ", " + value + ") - Error retrieving device" );
		$.Notification.notify('error','top left', 'Connection error', 'Could not retrieve data for light (' + ref + ')!');
	})
	.always(function() {
		console.log( timestamp() + " SplashHSDeviceUpdate(" + ref + ", " + value + ") - Done" );
	});
}



// Throttle per HS Device
// - run the first call, note the calling time
// - next call within the timeframe is not allowed, but the value stored and a call set with settimeout
// - next call within the timeframe cancels the previous call and sets the current call with the new value, 
//   ignoring the in-between value
// - 

function ThrottleSplashHSDeviceUpdate(ref, value) {
	console.log( timestamp() + " ThrottleSplashHSDeviceUpdate( " + ref + ", " + value + ")");

	const delay = 500;
	const now = (new Date()).getTime();
	if ( !Array.isArray( ThrottleSplashHSDeviceUpdate.refs ) ) {
		ThrottleSplashHSDeviceUpdate.refs = new Array();
	}
	if ( ref in ThrottleSplashHSDeviceUpdate.refs && typeof ThrottleSplashHSDeviceUpdate.refs[ ref ][ 'time' ] !== 'undefined' && ThrottleSplashHSDeviceUpdate.refs[ ref ][ 'time' ] + delay > now ) {
		// Throttle this call. Cancel previous calls and schedule this with new value
		console.log( timestamp() + " ThrottleSplashHSDeviceUpdate( " + ref + ", " + value + ") - throttling");
	    clearTimeout( ThrottleSplashHSDeviceUpdate.refs[ ref ].timerVar );
		ThrottleSplashHSDeviceUpdate.refs[ ref ].timerVar = setTimeout(function() { SplashHSDeviceUpdate( ref, value ); }, delay);
		ThrottleSplashHSDeviceUpdate.refs[ ref ].time = now;
	} else {
		// Run this call and register it
		console.log( timestamp() + " ThrottleSplashHSDeviceUpdate( " + ref + ", " + value + ") - executing");
		ThrottleSplashHSDeviceUpdate.refs[ ref ] = new Array();
		ThrottleSplashHSDeviceUpdate.refs[ ref ].time = now;
		SplashHSDeviceUpdate( ref, value );
	}
}



// Neato Robotics device update
function SplashNRRobotUpdate( serial, action ) {
	var jqxhr = $.getJSON( "assets/php/neato.controldevice.php?serial=" + serial + "&action=" + action, function() {
		console.log( timestamp() + " SplashNRRobotUpdate(" + serial + ", " + action + ") - Successful neato.controldevice jqxhr request" );
	})
	.done(function( data ) {
		console.log( timestamp() + " SplashNRRobotUpdate(" + data.serial + ", " + data.action + ") - Successful neato.controldevice jqxhr response" );
		// Retrieve the updated status
		CentralSplashUpdater.update( NRUpdateHandler.uidt, data.serial );
	})
	.fail(function( jqxhr, textStatus, error ) {
		console.log( timestamp() + " SplashNRRobotUpdate() - Error send action to Neato robot. " + textStatus + ", " + error );
		$.Notification.notify('error','top left', 'Connection error', 'Could not send action to Neato Robotics!' );
	})
	.always(function() {
		console.log( timestamp() + " SplashNRRobotUpdate.always() - Done" );
	});
}



// Throttle per Neato Device
// - run the first call, note the calling time
// - next call within the timeframe is not allowed, but the value stored and a call set with settimeout
// - next call within the timeframe cancels the previous call and sets the current call with the new value, 
//   ignoring the in-between value
// - 

function ThrottleSplashNRRobotUpdate( serial, action ) {
	console.log( timestamp() + " ThrottleSplashNRRobotUpdate( " + serial + ", " + action + ")");

	// Starting or resuming?
	if ( action === 'startCleaning' ) {
		var robot = NeatoRoboticsFactory.create( serial );
		if ( !robot.isCommandAvailable( 'start' ) && robot.isCommandAvailable( 'resume' ) ) {
			// switch
			action = 'resumeCleaning';
			console.log( timestamp() + " ThrottleSplashNRRobotUpdate( " + serial + ", " + action + ") - switching 'start' to 'resume'.");
		}
	}

	const delay = 500;
	const now = (new Date()).getTime();
	if ( !Array.isArray( ThrottleSplashNRRobotUpdate.serials ) ) {
		ThrottleSplashNRRobotUpdate.serials = new Array();
	}
	if ( serial in ThrottleSplashNRRobotUpdate.serials && typeof ThrottleSplashNRRobotUpdate.serials[ serial ][ 'time' ] !== 'undefined' && ThrottleSplashNRRobotUpdate.serials[ serial ][ 'time' ] + delay > now ) {
		// Throttle this call. Cancel previous calls and schedule this with new value
		console.log( timestamp() + " ThrottleSplashNRRobotUpdate( " + serial + ", " + action + ") - throttling");
	    clearTimeout( ThrottleSplashNRRobotUpdate.serials[ serial ].timerVar );
		ThrottleSplashNRRobotUpdate.serials[ serial ].timerVar = setTimeout(function() { SplashNRRobotUpdate( serial, action ); }, delay);
		ThrottleSplashNRRobotUpdate.serials[ serial ].time = now;
	} else {
		// Run this call and register it
		console.log( timestamp() + " ThrottleSplashHSDeviceUpdate( " + serial + ", " + action + ") - executing");
		ThrottleSplashNRRobotUpdate.serials[ serial ] = new Array();
		ThrottleSplashNRRobotUpdate.serials[ serial ].time = now;
		SplashNRRobotUpdate( serial, action );
	}
}

// Bose SoundTouch device update
function SplashSoundTouchUpdate( ip, action, volume = null, url = null, notification = null ) {
	var jqxhr = $.getJSON( "assets/php/bose.controldevice.php?ip=" + ip + "&action=" + action + ( volume != null ? '&volume=' + volume : '' ) + ( url != null ? '&url=' + url : '' ) + ( notification != null ? '&notification=' + notification : '' ), function() {
		console.log( timestamp() + " SplashSoundTouchUpdate(" + ip + ", " + action + ") - Successful bose.controldevice jqxhr request" );
	})
	.done(function( data ) {
		console.log( timestamp() + " SplashSoundTouchUpdate(" + data.ip + ", " + data.action + ") - Successful bose.controldevice jqxhr response" );
		if ( !( data.status !== 'undefined' && ( data.status == true || data.status == 'true' ) ) ) {
			// Successful interaction, but rejected request
			$.Notification.notify('warning','top left', 'Request could not be completed.', ip + " " + action);	
		}
		// Retrieve the updated status
		CentralSplashUpdater.update( BoseUpdateHandler.uidt, data.ip );
	})
	.fail(function( jqxhr, textStatus, error ) {
		console.log( timestamp() + " SplashSoundTouchUpdate() - Error send action to Bose SoundTouch. " + textStatus + ", " + error );
		$.Notification.notify('error','top left', 'Connection error', 'Could not send action to Bose SoundTouch!' );
	})
	.always(function() {
		console.log( timestamp() + " SplashSoundTouchUpdate.always() - Done" );
	});
}


// Throttle per Bose SoundTouch Device
// - run the first call, note the calling time
// - next call within the timeframe is not allowed, but the value stored and a call set with settimeout
// - next call within the timeframe cancels the previous call and sets the current call with the new value, 
//   ignoring the in-between value
// - 
function ThrottleSplashSoundTouchUpdate( ip, action, volume = null, url = null, notification = null  ) {
	console.log( timestamp() + " ThrottleSplashSoundTouchUpdate( " + ip + ", " + action + ")");
	var value = null;

	if ( action == 'TOGGLE_REPEAT' ) {
		var soundTouch = SoundTouchFactory.create( ip );
		action = ( soundTouch.isRepeatEnabled() ? 'REPEAT_OFF' : 'REPEAT_ALL' );
		console.log( timestamp() + " ThrottleSplashSoundTouchUpdate( " + ip + ", " + action + ") - switching 'TOGGLE_REPEAT' to '" + action + "'.");
	}
	if ( action == 'TOGGLE_SHUFFLE' ) {
		var soundTouch = SoundTouchFactory.create( ip );
		action = ( soundTouch.isShuffleEnabled() ? 'SHUFFLE_OFF' : 'SHUFFLE_ON' );
		console.log( timestamp() + " ThrottleSplashSoundTouchUpdate( " + ip + ", " + action + ") - switching 'TOGGLE_SHUFFLE' to '" + action + "'.");
	}
	if ( action == 'VOLUME_UP' ) {
		var soundTouch = SoundTouchFactory.create( ip );
		action = 'VOLUME';
		volume = Math.min( parseInt( soundTouch.getVolume() ) + 5, 100 );
		console.log( timestamp() + " ThrottleSplashSoundTouchUpdate( " + ip + ", " + action + ") - switching 'VOLUME_UP' to 'VOLUME' with value '" + volume + "'.");
	}
	if ( action == 'VOLUME_DOWN' ) {
		var soundTouch = SoundTouchFactory.create( ip );
		action = 'VOLUME';
		volume = Math.max( parseInt( soundTouch.getVolume() ) - 5, 0 );
		console.log( timestamp() + " ThrottleSplashSoundTouchUpdate( " + ip + ", " + action + ") - switching 'VOLUME_DOWN' to 'VOLUME' with value '" + volume + "'.");
	}

	const delay = 500;
	const now = (new Date()).getTime();
	if ( !Array.isArray( ThrottleSplashNRRobotUpdate.ips ) ) {
		ThrottleSplashSoundTouchUpdate.ips = new Array();
	}
	if ( ip in ThrottleSplashSoundTouchUpdate.ips && typeof ThrottleSplashSoundTouchUpdate.ips[ ip ][ 'time' ] !== 'undefined' && ThrottleSplashSoundTouchUpdate.ips[ ip ][ 'time' ] + delay > now ) {
		// Throttle this call. Cancel previous calls and schedule this with new value
		console.log( timestamp() + " ThrottleSplashSoundTouchUpdate( " + ip + ", " + action + ") - throttling");
	    clearTimeout( ThrottleSplashSoundTouchUpdate.ips[ ip ].timerVar );
		ThrottleSplashSoundTouchUpdate.ips[ ip ].timerVar = setTimeout(function() { SplashSoundTouchUpdate( ip, action, volume, url, notification ); }, delay);
		ThrottleSplashSoundTouchUpdate.ips[ ip ].time = now;
	} else {
		// Run this call and register it
		console.log( timestamp() + " ThrottleSplashSoundTouchUpdate( " + ip + ", " + action + ") - executing");
		ThrottleSplashSoundTouchUpdate.ips[ ip ] = new Array();
		ThrottleSplashSoundTouchUpdate.ips[ ip ].time = now;
		SplashSoundTouchUpdate( ip, action, volume, url, notification );
	}
}

// ----------------------- Audio file server (HTTP) for Bose SoundTouch notifications ------------------------------------------
var NotificationServer = {
	interval: 600000,	// Once every 10 minutes
	validationUrl: "assets/php/notificationserver.getstatus.php",
	available: false,
    callbacks: new Array(),
	setAvailability: function( available ) {
		if ( this.available == available ) {
			return; // ignore
		}
    	this.available = available;
    	// Notify callbacks of this change
    	this.notify();
	},
	isAvailable: function( ) {
    	return this.available;
	},
	getUrl: function( ) {
    	return this.validationUrl;
	},
	getInterval: function( ) {
    	return this.interval;
	},
    register: function( callback ) {
		console.log( timestamp() + " NotificationServer.register() - registering callback" );
		// add handler
		if ( this.callbacks.length == 0 ) {	// No need to check for undefined, created the array in init ( typeof this.callbacks !== 'undefined' )
		    // First callback, start the check
		    SplashFileserverAvailabilityCheck();
		}
	   	this.callbacks.push( callback );
    },
	notify: function ( ) {
		console.log( timestamp() + " NotificationServer.notifier() - calling callbacks" );
		$.each( this.callbacks, function( index, callback ) {
			// Make sure the callback is a function
			if (typeof callback === "function") {
				// Call it, since we have confirmed it is callable
				callback();
			}
		});
    },
};

// Checks if the php http server for serving the notification mp3 files is available
function SplashFileserverAvailabilityCheck( ) {
	var jqxhr = $.getJSON( NotificationServer.getUrl(), function() {
		console.log( timestamp() + " SplashFileserverAvailabilityCheck() - Successful status.json jqxhr request" );
	})
	.done(function( data ) {
		console.log( timestamp() + " SplashFileserverAvailabilityCheck() - Successful status.json jqxhr response" );
		if ( !( data.status !== 'undefined' && ( data.status == true || data.status == 'true' ) ) ) {
			// Successful interaction, but rejected request
			$.Notification.notify('error','top left', 'Notification server unavailable', 'Notification server not available. Notifications on SoundTouch not available.');
			NotificationServer.setAvailability( false );
		} else {
			NotificationServer.setAvailability( true );
		}
	})
	.fail(function( jqxhr, textStatus, error ) {
		console.error("getJSON failed, status: " + textStatus + ", error: "+error)
		alert( "getJSON failed, status: " + textStatus + ", error: "+error );
		console.log( timestamp() + " SplashFileserverAvailabilityCheck() - Not available." );
		$.Notification.notify('error','top left', 'Splash server not available', 'Splash server not available. Could not obtain Notifications server availability.');
		NotificationServer.setAvailability( false );
	})
	.always(function() {
		console.log( timestamp() + " SplashFileserverAvailabilityCheck.always() - Done" );
		setTimeout(function() { SplashFileserverAvailabilityCheck( ); }, NotificationServer.getInterval());
	});
}

/* --- Audi API --------------------------------------------------------- */

// Represents an Audi vehicle
function AudiVehicle ( vin ) {
    this.vin = vin;				// WAUZZZ8VXGA033557
    this.name;
	this.latitude = 0;
	this.longitude = 0;
	this.timestampCarCaptured = null;
	this.timestampCarSent = null;
	this.timestampCarSentUTC = null;
	this.parkingTimeUTC = null;
	this.avatar = "/assets/images/audi.png";
}
AudiVehicle.prototype.getUid = function() {				// To comply with CentralSplashUpdater
    return this.vin;
};
AudiVehicle.prototype.getValue = function() {
    return [ this.getLatitude(),this.getLongitude ];
};
AudiVehicle.prototype.getHandler = function() {
    return AudiUpdateHandler;
};
AudiVehicle.prototype.getVin = function() {
    return this.vin;
};
AudiVehicle.prototype.setName = function( name ) {
	this.name = name;
}
AudiVehicle.prototype.getName = function( ) {
	return this.name;
}
AudiVehicle.prototype.getLatitude = function() {
    return this.latitude;
};
AudiVehicle.prototype.setLatitude = function( latitude ) {
	if ( typeof latitude == "number" ) {
	    this.latitude = latitude;
	} else {
	    this.latitude = parseFloat( latitude );
	}
};
AudiVehicle.prototype.getLongitude = function() {
    return this.longitude;
};
AudiVehicle.prototype.setLongitude = function( longitude ) {
	if ( typeof longitude == "number" ) {
	    this.longitude = longitude;
	} else {
	    this.longitude = parseFloat( longitude );
	}
};
AudiVehicle.prototype.getTimestampCarCaptured = function() {
    return this.timestampCarCaptured;
};
AudiVehicle.prototype.setTimestampCarCaptured = function( timestampCarCaptured ) {	// 2018-03-19T19:56:18
	if ( timestampCarCaptured instanceof Date ) {
	    this.timestampCarCaptured = timestampCarCaptured;
	} else {
		var dt = timestampCarCaptured.split("T");
		var d = dt[0].split("-");
		var t = dt[1].split(":");
		this.timestampCarCaptured = new Date( d[0], (d[1]-1), d[2], t[0], t[1], t[2]);
	}
};
AudiVehicle.prototype.getTimestampCarSent = function() {
    return this.timestampCarSent;
};
AudiVehicle.prototype.setTimestampCarSent = function( timestampCarSent ) {	// 2018-03-19T19:56:18
	if ( timestampCarSent instanceof Date ) {
	    this.timestampCarSent = timestampCarSent;
	} else {
		var dt = timestampCarSent.split("T");
		var d = dt[0].split("-");
		var t = dt[1].split(":");
		this.timestampCarSent = new Date( d[0], (d[1]-1), d[2], t[0], t[1], t[2]);
	}
};
AudiVehicle.prototype.getTimestampCarSentUTC = function() {
    return this.timestampCarSentUTC;
};
AudiVehicle.prototype.setTimestampCarSentUTC = function( timestampCarSentUTC ) {	// 2018-03-19T18:55:22Z
	if ( timestampCarSentUTC instanceof Date ) {
	    this.timestampCarSentUTC = timestampCarSentUTC;
	} else {
		var dt = timestampCarSentUTC.split("T");
		var d = dt[0].split("-");
		var t = dt[1].split("Z");
		var t = t[0].split(":");
		this.timestampCarSentUTC = new Date( d[0], (d[1]-1), d[2], t[0], t[1], t[2]);
	}
};
AudiVehicle.prototype.getParkingTimeUTC = function() {
    return this.parkingTimeUTC;
};
AudiVehicle.prototype.setParkingTimeUTC = function( parkingTimeUTC ) {	// 2018-03-19T18:55:22Z
	if ( parkingTimeUTC instanceof Date ) {
	    this.parkingTimeUTC = parkingTimeUTC;
	} else {
		var dt = parkingTimeUTC.split("T");
		var d = dt[0].split("-");
		var t = dt[1].split("Z");
		var t = t[0].split(":");
		this.parkingTimeUTC = new Date( d[0], (d[1]-1), d[2], t[0], t[1], t[2]);
	}
};
AudiVehicle.prototype.getTimestampString = function( ) {
	const now = new Date( );
	var timestamp = this.timestampCarCaptured;
	if ( now.getFullYear() != timestamp.getFullYear() ) {
		return timestamp.getDate() + " " + MONTH_STR[nl_NL][timestamp.getMonth()] + " " + timestamp.getFullYear();
	}
	if ( now.getMonth() != timestamp.getMonth() ) {
		return timestamp.getDate() + " " + MONTH_STR[nl_NL][timestamp.getMonth()];
	}
	if ( now.getDate() != timestamp.getDate() ) {
		return timestamp.getDate() + " " + MONTH_STR[nl_NL][timestamp.getMonth()];
	}
	return timestamp.getHours() + ":" + (timestamp.getMinutes()<10?'0':'') + timestamp.getMinutes() + "u";
}
AudiVehicle.prototype.getParkingTimeString = function( ) {
	const now = new Date( );
	var timestamp = this.parkingTimeUTC;
	if ( now.getFullYear() != timestamp.getFullYear() ) {
		return timestamp.getDate() + " " + MONTH_STR[nl_NL][timestamp.getMonth()] + " " + timestamp.getFullYear();
	}
	if ( now.getMonth() != timestamp.getMonth() ) {
		return timestamp.getDate() + " " + MONTH_STR[nl_NL][timestamp.getMonth()];
	}
	if ( now.getDate() != timestamp.getDate() ) {
		return timestamp.getDate() + " " + MONTH_STR[nl_NL][timestamp.getMonth()];
	}
	return timestamp.getHours() + ":" + (timestamp.getMinutes()<10?'0':'') + timestamp.getMinutes() + "u";
}
AudiVehicle.prototype.getAvatar = function() {
    return this.avatar;
};


var AudiVehicleFactory = {
    vins: [],
    create: function( vin ) {
    	if ( !( vin in this.vins ) ) {
			// Create new
	    	this.vins[ vin ] = new AudiVehicle( vin );
		}
    	// Return newly created or existing one
    	return this.vins[ vin ];
    },
};




// ----------------------- Audi Vehicle Location Object ------------------------------------------
// Represents a Splash Audi Vehicle Location device
function SplashAudiVehicleMember ( vin ) {
    this.vehicle = AudiVehicleFactory.create( vin );
    // Element tot attach it to
    this.bindingElement = null;
	// Default width class. Works with col-lg-4 and col-lg-6
    this.widthClass = 'col-lg-6';
    this.zoom = 13;
	this.mapType = google.maps.MapTypeId.ROADMAP;
    this.zoom = 13;
    this.maps = [];
    this.mapDefault = true;
}

SplashAudiVehicleMember.prototype.getVehicle = function( ) {
	return this.vehicle;
}
SplashAudiVehicleMember.prototype.setBindingElement = function( bindingElement ) {
	this.bindingElement = bindingElement;
}
SplashAudiVehicleMember.prototype.getBindingElement = function( ) {
	return this.bindingElement;
}
SplashAudiVehicleMember.prototype.setName = function( name ) {
	this.vehicle.setName( name );
}
SplashAudiVehicleMember.prototype.getName = function( ) {
	return this.vehicle.getName();
}
SplashAudiVehicleMember.prototype.setMapType = function( mapType ) {
	this.mapType = mapType;
}
SplashAudiVehicleMember.prototype.getMapType = function( ) {
	return this.mapType;
}
SplashAudiVehicleMember.prototype.setZoom = function( zoom ) {
	this.zoom = zoom;
}
SplashAudiVehicleMember.prototype.getZoom = function( ) {
	return this.zoom;
}
SplashAudiVehicleMember.prototype.setWidthClass = function( widthClass ) {
	this.widthClass = widthClass;
}
SplashAudiVehicleMember.prototype.getWidthClass = function( ) {
	return this.widthClass;
}
SplashAudiVehicleMember.prototype.setMapDefault = function( mapDefault ) {
	this.mapDefault = mapDefault;
}
SplashAudiVehicleMember.prototype.getMapDefault = function( ) {
	return mapDefault;
}
SplashAudiVehicleMember.prototype.enableMap = function( map ) {
	this.maps[map] = true;
}
SplashAudiVehicleMember.prototype.disableMap = function( map ) {
	this.maps[map] = false;
}
SplashAudiVehicleMember.prototype.isMapEnabled = function( map, isStandardMap = false ) {
	return ( typeof this.maps[map] === 'undefined' && this.mapDefault && isStandardMap ) ||
		   ( typeof this.maps[map] !== 'undefined' && this.maps[map] == true );
}

SplashAudiVehicleMember.prototype.draw = function( ) {
	console.log( timestamp() + " SplashAudiVehicleMember.draw()");
	var vehicle = this.getVehicle();
	var vin = vehicle.getVin();
	
	// Does the element exist? No: draw, Yes: update
	if ( $('div#audi_' + vin).length ) {
		console.log( timestamp() + " SplashAudiVehicleMember.draw() - Update the element");

		$('#audi_' + vin + "_member_name b").html( vehicle.getName() );
		$('#audi_' + vin + "_member_timestamp").html( "update " +  vehicle.getTimestampString() + "." );
		$('#audi_' + vin + "_member_since").html( "Parked " + vehicle.getParkingTimeString() + ", last" );

		var mapTypeIds = [];
		for (var type in google.maps.MapTypeId) {
			if (this.isMapEnabled( type, true) ) {
				mapTypeIds.push(google.maps.MapTypeId[type]);
			}
		}
		if ( this.isMapEnabled( "OSM" ) || this.getMapType() == "OSM" ) {
			mapTypeIds.push( "OSM" );
		}
		if ( this.isMapEnabled( "CloudMade" ) || this.getMapType() == "CloudMade" ) {
			mapTypeIds.push( "CloudMade" );
		}	

		var map = new google.maps.Map(document.getElementById("audi_" + vin + "_map"), {
			center: new google.maps.LatLng( vehicle.getLatitude(), vehicle.getLongitude() ),
			zoom: this.getZoom(),
			mapTypeId: this.getMapType(),
			mapTypeControlOptions: {
				mapTypeIds: mapTypeIds
			}
		});

		map.mapTypes.set("OSM", new google.maps.ImageMapType({
			getTileUrl: function(coord, zoom) {
				// See above example if you need smooth wrapping at 180th meridian
				return "http://tile.openstreetmap.org/" + zoom + "/" + coord.x + "/" + coord.y + ".png";
			},
			tileSize: new google.maps.Size(256, 256),
			name: "OpenStreetMap",
			maxZoom: 18
		}));

		map.mapTypes.set("CloudMade", new google.maps.ImageMapType({
			getTileUrl: function(coord, zoom) {
				// See above example if you need smooth wrapping at 180th meridian
				return "http://b.tile.cloudmade.com/8ee2a50541944fb9bcedded5165f09d9/1/256/" + zoom + "/" + coord.x + "/" + coord.y + ".png";
			},
			tileSize: new google.maps.Size(256, 256),
			name: "CloudMade",
			maxZoom: 18
		}));

		new CustomMarker(new google.maps.LatLng(vehicle.getLatitude(), vehicle.getLongitude()), map, vehicle.getAvatar() );

	} else {
		// Element dows not exist, draw it
		console.log( timestamp() + " SplashLife360Member.draw() - Drawing new element");

		var elStr = `<div class="TOKEN_WIDTH_CLASS" id="audi_TOKEN_ID">
            <div class="card-box">
                <h4 id="audi_TOKEN_ID_member_name" style="display: inline-block;" class="m-t-0 m-b-20"><b class="header-title">...</b></h4>
                <h6 id="audi_TOKEN_ID_member_timestamp" class="life360_member_timestamp m-t-0 m-b-20" style="padding-top: 5px; padding-right: 7px; display: inline-block; float: right;"></h6>
                <h6 id="audi_TOKEN_ID_member_since" class="life360_member_since m-t-0 m-b-20" style="padding-top: 5px; padding-right: 7px; display: inline-block; float: right;"></h6>

                <div id="audi_TOKEN_ID_map" class="gmaps"></div>
            </div>
		</div>`;

		elStr = elStr.replace( /TOKEN_ID/g, vin );
		elStr = elStr.replace( /TOKEN_WIDTH_CLASS/g, this.getWidthClass() );
				
		$( this.getBindingElement() ).append( elStr );

		var obj = this;
		CentralSplashUpdater.register( vin, AudiUpdateHandler, function() { obj.draw() } )		
	}
}


/* --- Life360 --------------------------------------------------------- */

// Represents an Life360 location
function Life360Member ( id ) {
    this.id = id;
	this.latitude = 0;
	this.longitude = 0;
	this.accuracy = 0;
	this.since = 0;
	this.timestamp = 0;
	this.battery = 0;
	this.charging = false;
	this.firstname = "";
	this.lastname = "";
	this.avatar = "assets/images/users/avatar-unknown.png";
	this.wifi = false;
}
Life360Member.prototype.getUid = function() {					// To comply with CentralSplashUpdater
    return this.id;
};
Life360Member.prototype.getValue = function() {
    return [ this.getLatitude(), this.getLongitude ];
};
Life360Member.prototype.getHandler = function() {
    return Life360UpdateHandler;
};
Life360Member.prototype.getId = function() {
    return this.id;
};
Life360Member.prototype.getLatitude = function() {
    return this.latitude;
};
Life360Member.prototype.setLatitude = function( latitude ) {
	if ( typeof latitude == "number" ) {
	    this.latitude = latitude;
	} else {
	    this.latitude = parseFloat( latitude );
	}
};
Life360Member.prototype.getLongitude = function() {
    return this.longitude;
};
Life360Member.prototype.setLongitude = function( longitude ) {
	if ( typeof longitude == "number" ) {
	    this.longitude = longitude;
	} else {
	    this.longitude = parseFloat( longitude );
	}
};
Life360Member.prototype.getAccuracy = function() {
    return this.accuracy;
};
Life360Member.prototype.setAccuracy = function( accuracy ) {
	if ( typeof accuracy == "number" ) {
	    this.accuracy = accuracy;
	} else {
	    this.accuracy = parseInt( accuracy );
	}
};
Life360Member.prototype.getSince = function() {
    return this.since;
};
Life360Member.prototype.getSinceString = function() {
	const now = new Date( );
	const since = new Date( this.since * 1000 );
	if ( now.getFullYear() != since.getFullYear() ) {
		return since.getDate() + " " + MONTH_STR[nl_NL][since.getMonth()] + " " + since.getFullYear();
	}
	if ( now.getMonth() != since.getMonth() ) {
		return since.getDate() + " " + MONTH_STR[nl_NL][since.getMonth()];
	}
	if ( now.getDate() != since.getDate() ) {
		return since.getDate() + " " + MONTH_STR[nl_NL][since.getMonth()];
	}
	return since.getHours() + ":" + (since.getMinutes()<10?'0':'') + since.getMinutes() + "u";
}
Life360Member.prototype.setSince = function( since ) {
	if ( typeof since == "number" ) {
	    this.since = since;
	} else {
	    this.since = parseInt( since );
	}
};
Life360Member.prototype.getTimestamp = function() {
    return this.timestamp;
};
Life360Member.prototype.getTimestampString = function() {
	const now = new Date( );
	const timestamp = new Date( this.timestamp * 1000 );
	if ( now.getFullYear() != timestamp.getFullYear() ) {
		return timestamp.getDate() + " " + MONTH_STR[nl_NL][timestamp.getMonth()] + " " + timestamp.getFullYear();
	}
	if ( now.getMonth() != timestamp.getMonth() ) {
		return timestamp.getDate() + " " + MONTH_STR[nl_NL][timestamp.getMonth()];
	}
	if ( now.getDate() != timestamp.getDate() ) {
		return timestamp.getDate() + " " + MONTH_STR[nl_NL][timestamp.getMonth()];
	}
	return timestamp.getHours() + ":" + (timestamp.getMinutes()<10?'0':'') + timestamp.getMinutes() + "u";
}
Life360Member.prototype.setTimestamp = function( timestamp ) {
	if ( typeof since == "number" ) {
	    this.timestamp = timestamp;
	} else {
	    this.timestamp = parseInt( timestamp );
	}
};
Life360Member.prototype.getBattery = function() {
    return this.battery;
};
Life360Member.prototype.setBattery = function( battery ) {
	if ( typeof battery == "number" ) {
	    this.battery = battery;
	} else {
	    this.battery = parseInt( battery );
	}
};
Life360Member.prototype.isCharging = function() {
    return this.charging;
};
Life360Member.prototype.setCharging = function( charging ) {
	if ( typeof charging == "boolean" ) {
	    this.charging = charging;
	} else {
	    this.charging = (charging == 'true' || charging == '1');
	}
};
Life360Member.prototype.getFirstname = function() {
    return this.firstname;
};
Life360Member.prototype.setFirstname = function( firstname ) {
    this.firstname = firstname;
};
Life360Member.prototype.getLastname = function() {
    return this.lastname;
};
Life360Member.prototype.setLastname = function( lastname ) {
    this.lastname = lastname;
};
Life360Member.prototype.getName = function( ) {
    return (this.firstname + " " + this.lastname).trim();
};
Life360Member.prototype.getAvatar = function() {
    return this.avatar;
};
Life360Member.prototype.setAvatar = function( avatar ) {
    this.avatar = avatar;
};
Life360Member.prototype.hasWifi = function() {
    return this.wifi;
};
Life360Member.prototype.setWifi = function( wifi ) {
	if ( typeof wifi == "boolean" ) {
	    this.wifi = wifi;
	} else {
	    this.wifi = (wifi == 'true' || wifi == '1');
	}
};

var Life360MemberFactory = {
    ids: [],
    create: function( id ) {
    	if ( !( id in this.ids ) ) {
			// Create new
	    	this.ids[ id ] = new Life360Member( id );
		}
    	// Return newly created or existing one
    	return this.ids[ id ];
    },
};



// ----------------------- Life360 Location Object ------------------------------------------
// Represents a Splash Life360 Location device
function SplashLife360Member ( id ) {
    this.member = Life360MemberFactory.create( id );
    // Element tot attach it to
    this.bindingElement = null;
	// Default width class. Works with col-lg-4 and col-lg-6
    this.widthClass = 'col-lg-6';
    this.zoom = 13;
	this.mapType = google.maps.MapTypeId.ROADMAP;
    this.zoom = 13;
    this.maps = [];
    this.mapDefault = true;
}

SplashLife360Member.prototype.getMember = function( ) {
	return this.member;
}
SplashLife360Member.prototype.setBindingElement = function( bindingElement ) {
	this.bindingElement = bindingElement;
}
SplashLife360Member.prototype.getBindingElement = function( ) {
	return this.bindingElement;
}
SplashLife360Member.prototype.setMapType = function( mapType ) {
	this.mapType = mapType;
}
SplashLife360Member.prototype.getMapType = function( ) {
	return this.mapType;
}
SplashLife360Member.prototype.setZoom = function( zoom ) {
	this.zoom = zoom;
}
SplashLife360Member.prototype.getZoom = function( ) {
	return this.zoom;
}
SplashLife360Member.prototype.setWidthClass = function( widthClass ) {
	this.widthClass = widthClass;
}
SplashLife360Member.prototype.getWidthClass = function( ) {
	return this.widthClass;
}
SplashLife360Member.prototype.setMapDefault = function( mapDefault ) {
	this.mapDefault = mapDefault;
}
SplashLife360Member.prototype.getMapDefault = function( ) {
	return mapDefault;
}
SplashLife360Member.prototype.enableMap = function( map ) {
	this.maps[map] = true;
}
SplashLife360Member.prototype.disableMap = function( map ) {
	this.maps[map] = false;
}
SplashLife360Member.prototype.isMapEnabled = function( map, isStandardMap = false ) {
	return ( typeof this.maps[map] === 'undefined' && this.mapDefault && isStandardMap ) ||
		   ( typeof this.maps[map] !== 'undefined' && this.maps[map] == true );
}
SplashLife360Member.prototype.batteryIcon = function( battery ) {
	if ( battery > 89 ) {
		return '<i class="text-secondary">'+battery+'%</i> <i class="fa fa-battery-full text-success"></i>';
	}
	if ( battery > 69 ) {
		return '<i class="text-secondary">'+battery+'%</i> <i class="fa fa-battery-three-quarters text-success"></i>';
	}
	if ( battery > 49 ) {
		return '<i class="text-secondary">'+battery+'%</i> <i class="fa fa-battery-half   text-success"></i>';
	}
	if ( battery > 19 ) {
		return '<i class="text-secondary">'+battery+'%</i> <i class="fa fa-battery-quarter text-warning"></i>';
	}
	return '<i class="text-secondary">'+battery+'%</i> <i class="fa fa-battery-empty text-danger"></i>';
}
SplashLife360Member.prototype.chargingIcon = function( isCharging ) {
	if ( isCharging ) {
		return '<i class="fa fa-plug text-light"></i>';
	}
	return '';
}
SplashLife360Member.prototype.wifiIcon = function( hasWifi ) {
	if ( hasWifi ) {
		return '<i class="fa fa-wifi text-light"></i>';
	}
	return '';
}


SplashLife360Member.prototype.draw = function( ) {
	console.log( timestamp() + " SplashLife360Member.draw()");
	var member = this.getMember();
	var id = member.getId();
	
	// Does the element exist? No: draw, Yes: update
	if ( $('div#life360_' + id).length ) {
		console.log( timestamp() + " SplashLife360Member.draw() - Update the element");

		$('#life360_' + id + "_member_name b").html( member.getName() );
		$('#life360_' + id + "_member_battery").html( this.batteryIcon( member.getBattery() ) +  ' ' + this.chargingIcon( member.isCharging() ) );
		$('#life360_' + id + "_member_timestamp").html( "update " +  member.getTimestampString() + "." );
		$('#life360_' + id + "_member_since").html( "Sinds " + member.getSinceString() + ", last" );

		var mapTypeIds = [];
		for (var type in google.maps.MapTypeId) {
			if (this.isMapEnabled( type, true) ) {
				mapTypeIds.push(google.maps.MapTypeId[type]);
			}
		}
		if ( this.isMapEnabled( "OSM" ) || this.getMapType() == "OSM" ) {
			mapTypeIds.push( "OSM" );
		}
		if ( this.isMapEnabled( "CloudMade" ) || this.getMapType() == "CloudMade" ) {
			mapTypeIds.push( "CloudMade" );
		}	

		var map = new google.maps.Map(document.getElementById("life360_" + id + "_map"), {
			center: new google.maps.LatLng( member.getLatitude(), member.getLongitude() ),
			zoom: this.getZoom(),
			mapTypeId: this.getMapType(),
			mapTypeControlOptions: {
				mapTypeIds: mapTypeIds
			}
		});

		map.mapTypes.set("OSM", new google.maps.ImageMapType({
			getTileUrl: function(coord, zoom) {
				// See above example if you need smooth wrapping at 180th meridian
				return "http://tile.openstreetmap.org/" + zoom + "/" + coord.x + "/" + coord.y + ".png";
			},
			tileSize: new google.maps.Size(256, 256),
			name: "OpenStreetMap",
			maxZoom: 18
		}));

		map.mapTypes.set("CloudMade", new google.maps.ImageMapType({
			getTileUrl: function(coord, zoom) {
				// See above example if you need smooth wrapping at 180th meridian
				return "http://b.tile.cloudmade.com/8ee2a50541944fb9bcedded5165f09d9/1/256/" + zoom + "/" + coord.x + "/" + coord.y + ".png";
			},
			tileSize: new google.maps.Size(256, 256),
			name: "CloudMade",
			maxZoom: 18
		}));

		new CustomMarker(new google.maps.LatLng(member.getLatitude(), member.getLongitude()), map, member.getAvatar() );

	} else {
		// Element dows not exist, draw it
		console.log( timestamp() + " SplashLife360Member.draw() - Drawing new element");

		var elStr = `<div class="TOKEN_WIDTH_CLASS" id="life360_TOKEN_ID">
            <div class="card-box">
                <h4 id="life360_TOKEN_ID_member_name" style="display: inline-block;" class="m-t-0 m-b-20"><b class="header-title">...</b></h4>
                <h4 id="life360_TOKEN_ID_member_battery" style="display: inline-block; float: right;" class="m-t-0 m-b-20">...</h4>
                <h6 id="life360_TOKEN_ID_member_timestamp" class="life360_member_timestamp m-t-0 m-b-20" style="padding-top: 5px; padding-right: 7px; display: inline-block; float: right;"></h6>
                <h6 id="life360_TOKEN_ID_member_since" class="life360_member_since m-t-0 m-b-20" style="padding-top: 5px; padding-right: 7px; display: inline-block; float: right;"></h6>

                <div id="life360_TOKEN_ID_map" class="gmaps"></div>
            </div>
		</div>`;

		elStr = elStr.replace( /TOKEN_ID/g, id );
		elStr = elStr.replace( /TOKEN_WIDTH_CLASS/g, this.getWidthClass() );
				
		$( this.getBindingElement() ).append( elStr );

		var obj = this;
		CentralSplashUpdater.register( id, Life360UpdateHandler, function() { obj.draw() } );		
	}
}


//adapted from http://gmaps-samples-v3.googlecode.com/svn/trunk/overlayview/custommarker.html
function CustomMarker(latlng, map, imageSrc) {
    this.latlng_ = latlng;
    this.imageSrc = imageSrc;
    // Once the LatLng and text are set, add the overlay to the map.  This will
    // trigger a call to panes_changed which should in turn call draw.
    var obj = this;
    this.setMap(map);
}

CustomMarker.prototype = new google.maps.OverlayView();

CustomMarker.prototype.draw = function () {
    // Check if the div has been created.
    var div = this.div_;
    if (!div) {
        // Create a overlay text DIV
        div = this.div_ = document.createElement('div');
        // Create the DIV representing our CustomMarker
        div.className = "customMarker"

        var img = document.createElement("img");
        img.src = this.imageSrc;
        div.appendChild(img);
        google.maps.event.addDomListener(div, "click", function (event) {
            google.maps.event.trigger(me, "click");
        });

        // Then add the overlay to the DOM
        var panes = this.getPanes();
        panes.overlayImage.appendChild(div);
    }

    // Position the overlay 
    var point = this.getProjection().fromLatLngToDivPixel(this.latlng_);
    if (point) {
        div.style.left = point.x + 'px';
        div.style.top = point.y + 'px';
    }
};

CustomMarker.prototype.remove = function () {
    // Check if the overlay was on the map and needs to be removed.
    if (this.div_) {
        this.div_.parentNode.removeChild(this.div_);
        this.div_ = null;
    }
};

CustomMarker.prototype.getPosition = function () {
    return this.latlng_;
};





