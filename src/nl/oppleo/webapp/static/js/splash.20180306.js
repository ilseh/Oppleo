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
- bose device (https://developer.bose.com/soundtouch-control-api/apis)
  - voorkeursknoppen
  - wat speelt nu
  - speel over alle apparaten
- power toevoegen aan blokken (incl. uppdate), misschien geen getal maar wel een geel bliksem symbool?
- power
- energie
- camerabeeld (garage, ring)
- 

done:
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
var hsDevices = [[ 298, 'Woonkamer',	'SplashLightDevice',	null ],
 				 [ 377, 'Woonkamer',	'SplashLightDevice',	737  ], 
 				 [ 422, 'Woonkamer',	'SplashLightDevice',	null ], 
 				 [ 441, 'Keuken',		'SplashLightDevice',	null ], // Plafondspots
    		  	 [ 508, 'Gang', 		'SplashLightDevice',	null ],	// Designlamp
    		  	 [ 541, 'Voortuin', 	'SplashUptimeDevice',	null ],	// Ring Doorbell Pro
    		  	 [ 542, 'Meterkast', 	'SplashUptimeDevice',	null ],	// Ring Chime
    		  	 [ 544, 'Overloop 1e', 	'SplashUptimeDevice',	null ],	// Ring Chime
    		  	 [ 545, 'Overloop 2e', 	'SplashUptimeDevice',	null ],	// Ring Chime
    		  	 [ 598, 'Slaapkamer', 	'SplashLightDevice',	null ],	// Wandlampen
    		  	 [ 661, 'Inloopkast', 	'SplashLightDevice',	null ],	// Wandspots inloopkast
    		  	 [ 684, 'CV-ruimte', 	'SplashUptimeDevice',	null ],	// ASUS RT-AC66U
    		  	 [ 686, 'Badkamer 2', 	'SplashLightDevice',	null ],	// Badkamer led spots
    		  	 [ 697, 'Badkamer 2', 	'SplashFanDevice',		null ],	// Badkamer Fan Links 
    		  	 [ 699, 'Badkamer 2', 	'SplashFanDevice',		null ],	// Badkamer Fan Rechts
    		  	 [ 708, 'Badkamer 2',	'SplashTempDevice',		null ], // Temperatuur
    		  	 [ 709, 'Badkamer 2',	'SplashHumidDevice',	null ], // Luchtvochtigheid
    		  	 [ 730, 'Overloop 1e', 	'SplashUptimeDevice',	null ],	// Ubiquiti Unify UAP-AC-Pro
    		  	 [ 732, 'Woonkamer', 	'SplashUptimeDevice',	null ],	// Raspberry Pi
    		  	 [ 738, 'Woonkamer',	'SplashLightDevice',	null ],
    		  	 [ 740, 'Tuin',			'SplashTempDevice',		null ], // Tuintemperatuur
    		  	 [ 741, 'Tuin',			'SplashHumidDevice',	null ], // Tuin luchtvochtigheid
    		  	 [ 756, 'Slaapkamer',	'SplashEvohomeDevice',	null ], // Evohome
    		  	 [ 797, 'Woonkamer',	'SplashHarmonyDevice',	null ], // Harmony - Activity (1: PowerOff, 2: TV kijken, 3: Radio, 4: Flubbertje muziek, 5: Flubbertje, 6: iTV met Marantz, 7: Gramofon)
    		  	 [ 798, 'Woonkamer',	'SplashHarmonyDevice',	null ], // Harmony - TV ontvanger (1: PowerToggle, 2: 0, 3: 1, 4: 2, 5: 3, 6: 4, 7: 5, 8: 6, 9: 7, 10: 8, 11: 9, 12: Mute, 13: Channel Down, 14: ChannelUp, 15: DirectionDown, 16: DirectionLeft, 17: DirectionRight, 18: DirectionUp, 19: Select, 20: Stop, 21: Rewind, 22: Pause, 23: FastForward, 24: Record, 25: SlowForward, 26: Menu, 27: Teletext, 28: Green, 29: Red, 30: Blue, 31: Yellow, 32: Guide, 33: Info, 34: Cancel, 36: Radio, 39: TV)
    		  	 [ 799, 'Woonkamer',	'SplashHarmonyDevice',	null ], // Harmony - Receiver (1: PowerOff, 2: PowerOn, 16: Mute, 17: VolumeDown, 18: VolumeUp)
    		  	 [ 800, 'Woonkamer',	'SplashHarmonyDevice',	null ], // Harmony - ChromeCast Flubbertje
    		  	 [ 801, 'Woonkamer',	'SplashHarmonyDevice',	null ], // Harmony - TV (1: PowerOff, 2: PowerOn, 14: Mute, 15: VolumeDown, 16: VolumeUp, 41: AmbiLight, 42: AmbiMode)
    		  	 [ 802, 'Meterkast', 	'SplashUptimeDevice',	null ]	// ASUS RT-AC68U
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

function timestamp() {
	const now = new Date();
	return now.getFullYear() + "-" + (now.getMonth()<10?'0':'') + (now.getMonth()+1) + "-" + (now.getDate()<10?'0':'') + now.getDate() + '.' + (now.getHours()<10?'0':'') + now.getHours() + ":" + (now.getMinutes()<10?'0':'') + now.getMinutes() + "." + (now.getSeconds()<10?'0':'') + now.getSeconds() + '.' + now.getMilliseconds();
}

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


// ----------------------- Neato Robotics Object ------------------------------------------
// Central updater for Neato Robotics
// TODO: all robots are reported in a single status

var CentralNRUpdater = {
    serials: new Array(),
    interval: 60000,	// Use 1 minute
    isTerminated: false,
    getInterval: function() {
    	return this.interval;
    },
    setInterval: function( interval ) {
    	this.interval = interval;
    },
    register: function( serial, callback ) {
		console.log( timestamp() + " CentralNRUpdater.register() - registering callback for " + serial );
    	if ( !( serial in this.serials ) ) {
			// First entry, create array
		   	this.serials[ serial ] = new Array();
			// Add handler
		   	this.serials[ serial ].push( callback );
			// // This is a new location, start the updater for it
			CentralNRUpdater.update( serial );
    	} else {
			// Else just add handler
		   	this.serials[ serial ].push( callback );
    	}
    },
	terminate: function( isTerminated ) {
		this.isTerminated = isTerminated;
		// NOTE: setTimeout() returns a var, to be used with clearTimeout(myVar);
		//       when executed this var should be removed from a list
	},
	notify: function ( robot ) {
		console.log( timestamp() + " CentralNRUpdater.notifier() - calling callbacks for " + robot.getSerial() );
		$.each( this.serials[ robot.getSerial() ], function( index, callback ) {
			// Make sure the callback is a function
			if (typeof callback === "function") {
				// Call it, since we have confirmed it is callable
				callback( robot );
			}
		});
    },
    update: function ( serial ) {
    	if ( this.isTerminated ) {
    		return;
    	}
		var jqxhr = $.getJSON( "assets/php/neato.getstatus.php", function() {
			console.log( timestamp() + " CentralNRUpdater.update() - Successful request for " + serial );
		})
		.done(function( data ) {
//			console.log( timestamp() + " CentralNRUpdater.update() - Successful response for " + '' );
			console.log( data );

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
// XXXXX				
				// Now notify the callbacks
				CentralNRUpdater.notify( robot );
			});			
		})
		.fail(function( jqxhr, textStatus, error ) {
			console.log( timestamp() + " CentralNRUpdater.update() - Error retrieving robot with serial " + serial + ". " + textStatus + ", " + error );
			$.Notification.notify('error','top left', 'Connection error', 'Could not retrieve data from Neato Robotics!' );
		})
		.always(function() {
			console.log( timestamp() + " CentralNRUpdater.update() - Done " + serial + ", again in " + CentralNRUpdater.getInterval() );
			// Update again in x seconds
			setTimeout( function() { CentralNRUpdater.update( serial ) }, CentralNRUpdater.getInterval() );
		});
    }
}

// ----------------------- Evohome Zone Object ------------------------------------------
// Central updater for Evohome Zones

var CentralEHUpdater = {
    locationIds: new Array(),
    interval: 60000,	// Use 1 minute
    isTerminated: false,
    getInterval: function() {
    	return this.interval;
    },
    setInterval: function( interval ) {
    	this.interval = interval;
    },
    register: function( locationId, callback ) {
		console.log( timestamp() + " CentralEHUpdater.register() - registering callback for " + locationId );
    	if ( !( locationId in this.locationIds ) ) {
			// First entry, create array
		   	this.locationIds[ locationId ] = new Array();
			// Add handler
		   	this.locationIds[ locationId ].push( callback );
			// // This is a new location, start the updater for it
			CentralEHUpdater.update( locationId );
    	} else {
			// Else just add handler
		   	this.locationIds[ locationId ].push( callback );
    	}
    },
	terminate: function( isTerminated ) {
		this.isTerminated = isTerminated;
		// NOTE: setTimeout() returns a var, to be used with clearTimeout(myVar);
		//       when executed this var should be removed from a list
	},
	notify: function ( locationObj ) {
		console.log( timestamp() + " CentralEHUpdater.notifier() - calling callbacks for " + locationObj.getLocationId() );
		$.each( this.locationIds[ locationObj.getLocationId() ], function( index, callback ) {
			// Make sure the callback is a function
			if (typeof callback === "function") {
				// Call it, since we have confirmed it is callable
				callback( locationObj );
			}
		});
    },
    update: function ( locationId ) {
    	if ( this.isTerminated ) {
    		return;
    	}
		var jqxhr = $.getJSON( "assets/php/evohome.getstatus.php", function() {
			console.log( timestamp() + " CentralEHUpdater.update() - Successful request for " + locationId );
		})
		.done(function( data ) {
			console.log( timestamp() + " CentralEHUpdater.update() - Successful response" );	// TODO for?
			console.log( data );

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
			CentralEHUpdater.notify( locationObj );
		})
		.fail(function() {
			console.log( timestamp() + " CentralEHUpdater.update() - Error retrieving location " + locationId );
			$.Notification.notify('error','top left', 'Connection error', 'Could not retrieve data!');
		})
		.always(function() {
			console.log( timestamp() + " CentralEHUpdater.update() - Done " + locationId + ", again in " + CentralEHUpdater.getInterval() );
			// Update again in x seconds
			setTimeout( function() { CentralEHUpdater.update( locationId ) }, CentralEHUpdater.getInterval() );
		});
    }
}

// ----------------------- Light Device Object ------------------------------------------
// Central updater for HomeSeer Devices

var CentralHSUpdater = {
    refs: new Array(),
    refsHandle: new Array(),
    refsLastrun: new Array(),
    interval: 5000,	// For now one interval for all
    isTerminated: false,
    getInterval: function() {
    	return this.interval;
    },
    setInterval: function( interval ) {
    	this.interval = interval;
    },
    register: function( ref, callback ) {
		console.log( timestamp() + " CentralHSUpdater.register() - registering callback for " + ref );
    	if ( !( ref in this.refs ) ) {
			// First entry, create array
		   	this.refs[ ref ] = new Array();
			// Add handler
		   	this.refs[ ref ].push( callback );
			// // This is a new ref, start the updater for it
			CentralHSUpdater.update( ref );
    	} else {
			// Else just add handler
		   	this.refs[ ref ].push( callback );
    	}
    },
	terminate: function( isTerminated ) {
		this.isTerminated = isTerminated;
		$.each( this.refsHandle, function( handle ) {
			clearTimeout( handle );
		});
		this.refsHandle = new Array();
	},
	notify: function ( hsDev ) {
		console.log( timestamp() + " CentralHSUpdater.notifier() - calling callbacks for " + hsDev.getRef() );
		$.each( this.refs[ hsDev.getRef() ], function( index, callback ) {
			// Make sure the callback is a function
			if (typeof callback === "function") {
				// Call it, since we have confirmed it is callable
				callback( hsDev );
			}
		});
    },
	setHandle: function( ref, handle ) {
		this.refsHandle[ ref ] = handle;
	},
	setLastrun: function( ref, ts ) {
		this.refsLastrun[ ref ] = ts;
	},
    update: function( ref, extra = false ) {
		if ( this.isTerminated ) {
			return;
    	}
		var jqxhr = $.getJSON( "assets/php/homeseer.getstatus.php?ref=" + ref, function() {
			console.log( timestamp() + " CentralHSUpdater.update() - Successful request for " + ref );
			CentralHSUpdater.setLastrun( ref, timestamp() );

		})
		.done(function( data ) {
			var ref = getKeyInObject( data, 'ref' );
			console.log( timestamp() + " CentralHSUpdater.update() - Successful response for " + ref );
			console.log( data );
if (ref == 699) {
	console.log('here');
}
			var hsDev = HSDeviceFactory.create( ref );
			hsDev.setName( getKeyInObject( data, 'name' ) );
			hsDev.setValue( getKeyInObject( data, 'value' ) );
			if ( ref == 463 ) {	// Smoke sensor
				if ( hsDev.getValue() > 100 ) { hsDev.setValue( 0 ); }			
			}
			hsDev.setStatus( getKeyInObject( data, 'status' ) );
			hsDev.setLastChangeHS( getKeyInObject( data, 'last_change' ) );
			hsDev.setLocation( getKeyInObject( data, 'location' ) );
			hsDev.setLocation2( getKeyInObject( data, 'location2' ) );
			hsDev.setType( getKeyInObject( data, 'device_type_string' ) );
			
			// Now notify the callbacks
			CentralHSUpdater.notify( hsDev );
		})
		.fail(function() {
			console.log( timestamp() + " CentralHSUpdater.update() - Error retrieving device " + ref );
			$.Notification.notify('error','top left', 'Connection error', 'Could not retrieve data!');
		})
		.always(function() {
			console.log( timestamp() + " CentralHSUpdater.update() - Done " + ref + ", again in " + CentralHSUpdater.getInterval() );
			// Update again in x seconds, if not an extra update request
			if ( !extra ) {
				var handle = setTimeout( function() { CentralHSUpdater.update( ref ) }, CentralHSUpdater.getInterval() );
				CentralHSUpdater.setHandle( ref, handle );
			}
		});
    }
}


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

HSDevice.prototype.getRef = function() {
    return this.ref;
};
HSDevice.prototype.getName = function() {
    return this.name;
};
HSDevice.prototype.setName = function( name ) {
    this.name = name;
};
HSDevice.prototype.getValue = function() {
    return this.value;
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
	return monthToStr( nl_NL, this.lastChange.getMonth() ) + " " + this.lastChange.getDate() + ", " + this.lastChange.getFullYear();   
};
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

// ----------------------- Neato Robot ------------------------------------------

// Represents an Evohome location
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


// ----------------------- Harmony Device Object ------------------------------------------
// Represents a Splash Harmony device
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
			switch( robot.getError() ) {
				case 'ui_error_brush_stuck':
					$('h3#nrr_' + serial + '_activity_text').html("Borstel vastgelopen");
					break;
				case 'ui_error_vacuum_stuck':
					$('h3#nrr_' + serial + '_activity_text').html("Vastgelopen");
					break;
				case 'ui_error_dust_bin_full':
					$('h3#nrr_' + serial + '_activity_text').html("Afvalbak vol");
					break;
				default:
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
					$('h3#nrr_' + serial + '_activity_text').html("Started");
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
		$( "div#nrr_OPS29117-508CB1BE3FC7_schedule h6" ).remove( );
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
//		$( this.getBindingElement() ).append('<div class="col-lg-3 col-md-6" id="std_'+ref+'"><div class="widget-bg-color-icon card-box"><div class="bg-icon bg-icon-warning pull-left"><i class="fa fa-thermometer-3 text-primary"></i></div><div class="text-right"><h3 id="std_'+ref+'_status" class="text-primary m-t-10">--%</h3><h7 id="std_'+ref+'_name" class="text-dark m-t-10">--</h7><p id="std_'+ref+'_location" class="text-muted mb-0 blockquote-reverse">--</p><div class="clearfix"></div></div></div>');

		var obj = this;
		$('#nrr_' + serial + '_schedule_myonoffswitch').change( obj.switchScheduleOnOff );
		// Register for updates. Bind the callback to this object
		var obj = this;
		CentralNRUpdater.register( serial, function() { obj.draw() } );
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
function SplashHarmonyDevice ( ref ) {
    this.hsdev = HSDeviceFactory.create( ref );
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

SplashHarmonyDevice.prototype.draw = function( ) {
	console.log( timestamp() + " SplashHarmonyDevice.draw()");
	var hsDev = this.getHSDev();
	var ref = hsDev.getRef();
	// Remove the spinner
	$('#slhd_797_activity_refresh_button').addClass('btn-outline-secondary');
	$('#slhd_797_activity_refresh_button').removeClass('btn-secondary'); 
	$('#slhd_797_activity_refresh').removeClass('fa-spin');
	// Does the element exist? No: draw, Yes: update
	if ( $('div#slhd_' + ref).length ) {
		console.log( timestamp() + " SplashHarmonyDevice.draw() - Update the element");

		// Harmony - Activity (1: PowerOff, 2: TV kijken, 3: Radio, 4: Flubbertje muziek, 5: Flubbertje, 6: iTV met Marantz, 7: Gramofon)
		$('button#slhd_797_tv').removeClass('btn-warning');			$('button#slhd_797_tv').addClass('btn-outline-warning');
		$('button#slhd_797_spotify').removeClass('btn-success');	$('button#slhd_797_spotify').addClass('btn-outline-success');
		$('button#slhd_797_radio').removeClass('btn-info');			$('button#slhd_797_radio').addClass('btn-outline-info');
		$('button#slhd_797_off').removeClass('btn-light');			$('button#slhd_797_off').addClass('btn-outline-light');
		switch ( hsDev.getValue() ) {
			case 7:		// Gramofon
				$('div#slhd_tvpresets').slideUp();
				$('div#slhd_radiopresets').slideUp();
				$('div#slhd_colorbuttons').slideUp();
				$('div#slhd_videocontrols').slideUp();
				$('div#slhd_updownleftrightcontrols').slideUp();
				$('div#slhd_volumecontrols').slideDown();
				$('div#slhd_exitguidecontrols').slideUp();
				$('button#slhd_797_spotify').addClass('btn-success');
				$('button#slhd_797_spotify').removeClass('btn-outline-success');
				$('h3#slhd_797_activity_text').html('Gramofon');
				break;
			case 6:		// iTV met Marantz
				$('div#slhd_tvpresets').slideUp();
				$('div#slhd_radiopresets').slideUp();
				$('div#slhd_colorbuttons').slideUp();
				$('div#slhd_videocontrols').slideDown();
				$('div#slhd_updownleftrightcontrols').slideDown();
				$('div#slhd_volumecontrols').slideDown();
				$('div#slhd_exitguidecontrols').slideDown();
				$('h3#slhd_797_activity_text').html('iTV met Marantz');
				break;
			case 5:		// Flubbertje
				$('div#slhd_tvpresets').slideUp();
				$('div#slhd_radiopresets').slideUp();
				$('div#slhd_colorbuttons').slideUp();
				$('div#slhd_videocontrols').slideUp();
				$('div#slhd_updownleftrightcontrols').slideUp();
				$('div#slhd_volumecontrols').slideDown();
				$('div#slhd_exitguidecontrols').slideUp();
				$('h3#slhd_797_activity_text').html('Flubbertje');
				break;
			case 4:		// Flubbertje muziek
				$('div#slhd_tvpresets').slideUp();
				$('div#slhd_radiopresets').slideUp();
				$('div#slhd_colorbuttons').slideUp();
				$('div#slhd_videocontrols').slideUp();
				$('div#slhd_updownleftrightcontrols').slideUp();
				$('div#slhd_volumecontrols').slideDown();
				$('div#slhd_exitguidecontrols').slideUp();
				$('h3#slhd_797_activity_text').html('Flubbertje muziek');
				break;
			case 3:		// Radio
				$('div#slhd_tvpresets').slideUp();
				$('div#slhd_radiopresets').slideDown();
				$('div#slhd_colorbuttons').slideUp();
				$('div#slhd_videocontrols').slideUp();
				$('div#slhd_updownleftrightcontrols').slideUp();
				$('div#slhd_volumecontrols').slideDown();
				$('div#slhd_exitguidecontrols').slideUp();
				$('button#slhd_797_radio').addClass('btn-info');
				$('button#slhd_797_radio').removeClass('btn-outline-info');
				$('h3#slhd_797_activity_text').html('Radio');
				break;
			case 2:		// TV kijken
				$('div#slhd_tvpresets').slideDown();
				$('div#slhd_radiopresets').slideUp();
				$('div#slhd_colorbuttons').slideDown();
				$('div#slhd_videocontrols').slideDown();
				$('div#slhd_updownleftrightcontrols').slideDown();
				$('div#slhd_volumecontrols').slideDown();
				$('div#slhd_exitguidecontrols').slideDown();
				$('button#slhd_797_tv').addClass('btn-warning');
				$('button#slhd_797_tv').removeClass('btn-outline-warning');
				$('h3#slhd_797_activity_text').html('TV kijken');
				break;
			case 1:		// PowerOff
				$('div#slhd_tvpresets').slideUp();
				$('div#slhd_radiopresets').slideUp();
				$('div#slhd_colorbuttons').slideUp();
				$('div#slhd_videocontrols').slideUp();
				$('div#slhd_updownleftrightcontrols').slideUp();
				$('div#slhd_volumecontrols').slideUp();
				$('div#slhd_exitguidecontrols').slideUp();
				$('button#slhd_797_off').addClass('btn-light');
				$('button#slhd_797_off').removeClass('btn-outline-light');
				$('h3#slhd_797_activity_text').html('UIT');
				break;
			default:
				$('div#slhd_tvpresets').slideUp();
				$('div#slhd_radiopresets').slideUp();
				$('div#slhd_colorbuttons').slideUp();
				$('div#slhd_videocontrols').slideUp();
				$('div#slhd_updownleftrightcontrols').slideUp();
				$('div#slhd_volumecontrols').slideUp();
				$('div#slhd_exitguidecontrols').slideUp();
				$('h3#slhd_797_activity_text').html('...');
				break;				
		}


	} else {
		// Element dows not exist, draw it
		console.log( timestamp() + " SplashHarmonyDevice.draw() - Drawing new element");
//		$( this.getBindingElement() ).append('<div class="col-lg-3 col-md-6" id="std_'+ref+'"><div class="widget-bg-color-icon card-box"><div class="bg-icon bg-icon-warning pull-left"><i class="fa fa-thermometer-3 text-primary"></i></div><div class="text-right"><h3 id="std_'+ref+'_status" class="text-primary m-t-10">--%</h3><h7 id="std_'+ref+'_name" class="text-dark m-t-10">--</h7><p id="std_'+ref+'_location" class="text-muted mb-0 blockquote-reverse">--</p><div class="clearfix"></div></div></div>');


		// Register for updates. Bind the callback to this object
		var obj = this;
		CentralHSUpdater.register( ref, function() { obj.draw() } );
	}
}

SplashHarmonyDevice.prototype.volumeUp = function( ) {
	var hsDev = this.getHSDev();
	if ( [ 3, 7 ].includes(hsDev.getValue()) ) {	// Radio, Gramofon
		SplashHSDeviceUpdate( 799, 18 );			// Volume Up on Receiver [799]
	}
	if ( [ 2 ].includes(hsDev.getValue()) ) {		// TV Kijken
		SplashHSDeviceUpdate( 801, 16 );			// Volume Up on TV [801]
	}
}

SplashHarmonyDevice.prototype.volumeDown = function( ) {
	var hsDev = this.getHSDev();
	if ( [ 3, 7 ].includes(hsDev.getValue()) ) {	// Radio, Gramofon
		SplashHSDeviceUpdate( 799, 17 );			// Volume Down on Receiver [799]
	}
	if ( [ 2 ].includes(hsDev.getValue()) ) {		// TV Kijken
		SplashHSDeviceUpdate( 801, 15 );			// Volume Down on TV [801]
	}
}

SplashHarmonyDevice.prototype.mute = function( ) {
	var hsDev = this.getHSDev();
	if ( [ 3, 7 ].includes(hsDev.getValue()) ) {	// Radio, Gramofon
		SplashHSDeviceUpdate( 799, 16 );			// Mute on Receiver [799]
	}
	if ( [ 2 ].includes(hsDev.getValue()) ) {		// TV Kijken
		SplashHSDeviceUpdate( 801, 14 );			// Mute on TV [801]
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
		$( this.getBindingElement() ).append('<div class="'+this.getWidthClass()+'" id="sehd_'+zoneId+'"><div class="card-box eh-card-box"><div class="eh-logo"><img src="assets/images/honeywell-evohome-logo.png"></div><div class="eh-heat-box"><h3 id="sehd_'+zoneId+'_heat_tag" class="m-t-2 eh-heat-val"><b id="sehd_'+zoneId+'_heat" class="counter">0</b>&#8451;</h3><h6 class="text-muted eh-heat">Heatpoint</h6></div><div class="eh-temp-box"><h6 id="sehd_'+zoneId+'_temp_tag" class="text-muted eh-temp-val"><b id="sehd_'+zoneId+'_temp" class="counter">0</b>&#8451;</h6><h6 class="text-muted eh-temp">Temp</h6></div><div><label class="control-label m-t-30 m-l-5"><b id="sehd_'+zoneId+'_location">--</b></label></div><div class="btn-group m-b-10 m-t-10 m-l-10"><button type="button" id="sehd_'+zoneId+'_5" class="sbrdb_late btn btn-outline-info btn-sm waves-effect waves-light"><span>5&#8451;</span></button><button type="button" id="sehd_'+zoneId+'_15" class="sbrdb_late btn btn-outline-info btn-sm waves-effect waves-light"><span>15&#8451;</span></button><button type="button" id="sehd_'+zoneId+'_17" class="sbrdb_late btn btn-outline-success btn-sm waves-effect waves-light"><span>17&#8451;</span></button><button type="button" id="sehd_'+zoneId+'_20" class="sbrdb_late btn btn-outline-warning btn-sm waves-effect waves-light"><span>20&#8451;</span></button><button type="button" id="sehd_'+zoneId+'_21" class="sbrdb_late btn btn-outline-warning btn-sm waves-effect waves-light"><span>21&#8451;</span></button><button type="button" id="sehd_'+zoneId+'_22" class="sbrdb_late btn btn-outline-danger btn-sm waves-effect waves-light"><span>22&#8451;</span></button></div><div class="btn-group-vertical m-b-10 eh-updown"><button type="button" id="sehd_'+zoneId+'_plus" class="sbrdb_plus btn btn-light btn-sm waves-effect waves-light"> <i class="fa fa-chevron-up m-r-5"></i> </button><button type="button" id="sehd_'+zoneId+'_min" class="sbrdb_min btn btn-outline-light btn-sm waves-effect waves-light"> <i class="fa fa-chevron-down m-r-5"> </i> </button></div></div></div>');

		$('button#sehd_'+zoneId+'_5').on("click", function () {
			console.log( timestamp() + " SplashEvohomeZone.draw() - " + ehZone.getName() + " ["+zoneId+"] to 5");
			ehZone.setTargetTemperature( 5 );
			ThrottleSplashEHZoneSetpointUpdate( zoneId, 5, 'FollowSchedule', '' );
			CentralEHUpdater.notify( ehLocation );
		});
		$('button#sehd_'+zoneId+'_15').on("click", function () {
			console.log( timestamp() + " SplashEvohomeZone.draw() - " + ehZone.getName() + " ["+zoneId+"] to 15");
			ehZone.setTargetTemperature( 15 );
			ThrottleSplashEHZoneSetpointUpdate( zoneId, 15, 'FollowSchedule', '' );
			CentralEHUpdater.notify( ehLocation );
		});
		$('button#sehd_'+zoneId+'_17').on("click", function () {
			console.log( timestamp() + " SplashEvohomeZone.draw() - " + ehZone.getName() + " ["+zoneId+"] to 17");
			ehZone.setTargetTemperature( 17 );
			ThrottleSplashEHZoneSetpointUpdate( zoneId, 17, 'FollowSchedule', '' );
			CentralEHUpdater.notify( ehLocation );
		});
		$('button#sehd_'+zoneId+'_20').on("click", function () {
			console.log( timestamp() + " SplashEvohomeZone.draw() - " + ehZone.getName() + " ["+zoneId+"] to 20");
			ehZone.setTargetTemperature( 20 );
			ThrottleSplashEHZoneSetpointUpdate( zoneId, 20, 'FollowSchedule', '' );
			CentralEHUpdater.notify( ehLocation );
		});
		$('button#sehd_'+zoneId+'_21').on("click", function () {
			console.log( timestamp() + " SplashEvohomeZone.draw() - " + ehZone.getName() + " ["+zoneId+"] to 21");
			ehZone.setTargetTemperature( 21 );
			ThrottleSplashEHZoneSetpointUpdate( zoneId, 21, 'FollowSchedule', '' );
			CentralEHUpdater.notify( ehLocation );
		});
		$('button#sehd_'+zoneId+'_22').on("click", function () {
			console.log( timestamp() + " SplashEvohomeZone.draw() - " + ehZone.getName() + " ["+zoneId+"] to 22");
			ehZone.setTargetTemperature( 22 );
			ThrottleSplashEHZoneSetpointUpdate( zoneId, 22, 'FollowSchedule', '' );
			CentralEHUpdater.notify( ehLocation );
		});
		$('button#sehd_'+zoneId+'_plus').on("click", function () {
			var heatpoint = Math.min( parseFloat( $('b#sehd_'+zoneId+'_heat').text() ) + .5, 25 );
			console.log( timestamp() + " SplashEvohomeZone.draw() - " + ehZone.getName() + " ["+zoneId+"] Plus to " + heatpoint);
			ehZone.setTargetTemperature( heatpoint );
			ThrottleSplashEHZoneSetpointUpdate( zoneId, heatpoint, 'FollowSchedule', '' );
			CentralEHUpdater.notify( ehLocation );
		});
		$('button#sehd_'+zoneId+'_min').on("click", function () {
			var heatpoint = Math.max( parseFloat(  $('b#sehd_'+zoneId+'_heat').text() ) - .5, 5 );
			console.log( timestamp() + " SplashEvohomeZone.draw() - " + ehZone.getName() + " ["+zoneId+"] Min to " + heatpoint);
			ehZone.setTargetTemperature( heatpoint );
			ThrottleSplashEHZoneSetpointUpdate( zoneId, heatpoint, 'FollowSchedule', '' );
			CentralEHUpdater.notify( ehLocation );
		});
		// Register for updates. Bind the callback to this object
		var obj = this;
		CentralEHUpdater.register( ehLocation.getLocationId(), function() { obj.draw() } );
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
}

SplashBedroomDevice.prototype.setBindingElement = function( bindingElement ) {
	this.bindingElement = bindingElement;
}
SplashBedroomDevice.prototype.getBindingElement = function( ) {
	return this.bindingElement;
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
		$( this.getBindingElement() ).append('<div class="col-12" id="sbrd"><div class="card-box"><form class="form-horizontal"><div class="form-group"><label for="slrd_slider" class="control-label"><b>Slaapkamer</b> <span class="font-normal text-muted clearfix">dimmer</span></label><div class="m-b-20"><input type="text" id="sbrd_slider"></div><div><div class="sbrdb_activity_wrapper"><div class="btn-group m-b-10"><button type="button" class="sbrdb_on btn btn-light waves-effect"> <i class="fa  fa-toggle-on m-r-5"></i> <span>Aan</span></button><button type="button" class="sbrdb_off btn btn-outline-light waves-effect waves-dark"> <i class="fa  fa-toggle-off m-r-5"></i> <span>Uit</span></button></div>&nbsp;<div class="btn-group m-b-10"><button type="button" class="sbrdb_plus btn btn-light waves-effect waves-light"> <i class="fa fa-chevron-up m-r-5"></i> </button><button type="button" class="sbrdb_min btn btn-outline-light waves-effect waves-light"> <i class="fa fa-chevron-down m-r-5"> </i> </button></div>&nbsp;<div class="btn-group m-b-10"><button type="button" class="sbrdb_late btn btn-outline-info waves-effect waves-light"><i class="fa fa-television m-r-5"></i> <span>Laat</span></button><button type="button" class="sbrdb_bright btn btn-outline-danger waves-effect waves-light"><i class="fa fa-sun-o m-r-5"></i> <span>Bright</span></button></div></div></div> </div></form></div></div>');
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
//				CentralHSUpdater.notify( hsDev );
	        },
	        onUpdate: function (data) {
				console.log( timestamp() + ' ---> Slider Bedroom updated');
	        }
	    });
		// Register for updates. Bind the callback to this object
		var obj = this;
		CentralHSUpdater.register( 598, function() { obj.draw() } );
	}

}

SplashBedroomDevice.prototype.setValue = function( value ) {
	var hsDev = HSDeviceFactory.create( 598 );
	hsDev.setValue( value );
	ThrottleSplashHSDeviceUpdate( 598, value );						// Wandlampen
	CentralHSUpdater.notify( HSDeviceFactory.create( 598 ) );
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
		$( this.getBindingElement() ).append('<div class="' + this.getWidthClass() + '" id="slrd"><div class="card-box"><form class="form-horizontal"><div class="form-group"><label for="slrd_slider" class="control-label"><b>Woonkamer</b> <span class="font-normal text-muted clearfix">dimmer</span></label><div class="m-b-20"><input type="text" id="slrd_slider"></div><div><div class="slrdb_activity_wrapper"><div class="btn-group m-b-10"><button type="button" id="slrdb_on" class="slrdb_on btn btn-light waves-effect"> <i class="fa fa-toggle-on m-r-5"></i> <span>Aan</span></button><button type="button" id="slrdb_off" class="slrdb_off btn btn-outline-light waves-effect waves-dark"> <i class="fa fa-toggle-off m-r-5"></i> <span>Uit</span></button></div>&nbsp;<div class="btn-group m-b-10"><button type="button" id="slrdb_plus" class="slrdb_plus btn btn-light waves-effect waves-light"> <i class="fa fa-chevron-up m-r-5"></i> </button><button type="button" id="slrdb_min" class="slrdb_min btn btn-outline-light waves-effect waves-light"> <i class="fa fa-chevron-down m-r-5"> </i> </button></div>&nbsp;<div class="btn-group m-b-10"><button type="button" id="slrdb_movie" class="slrdb_movie btn btn-outline-info waves-effect waves-light"><i class="fa fa-television m-r-5"></i> <span>Film</span></button><button type="button" id="slrdb_entertain" class="slrdb_entertain btn btn-outline-success waves-effect waves-light"><i class="fa fa-comments m-r-5"></i> <span>Visite</span></button><button type="button" id="slrdb_kook" class="slrdb_kook btn btn-outline-warning waves-effect waves-light"><i class="fa fa-search m-r-5"></i> <span>Koken</span></button><button type="button" id="slrdb_bright" class="slrdb_bright btn btn-outline-danger waves-effect waves-light"><i class="fa fa-sun-o m-r-5"></i> <span>Bright</span></button></div></div></div> </div></form></div></div>');
		var slrdObj = this;
		$("button#slrdb_on").on("click", function () {
			var $range = $("#slrd_slider");
			var slider = $range.data("ionRangeSlider");
		    slider.update({
		        from: 50
		    });
		    slrdObj.setValue( 50 );
		});
		$("button#slrdb_off").on("click", function () {
			var $range = $("#slrd_slider");
			var slider = $range.data("ionRangeSlider");
		    slider.update({
		        from: 0
		    });
		    slrdObj.setValue( 0 );
		});
		$("button#slrdb_movie").on("click", function () {
			var $range = $("#slrd_slider");
			var slider = $range.data("ionRangeSlider");
		    slider.update({
		        from: 40
		    });
		    slrdObj.setValue( 40 );
		});
		$("button#slrdb_entertain").on("click", function () {
			var $range = $("#slrd_slider");
			var slider = $range.data("ionRangeSlider");
		    slider.update({
		        from: 50
		    });
		    slrdObj.setValue( 50 );
		});
		$("button#slrdb_kook").on("click", function () {
			var $range = $("#slrd_slider");
			var slider = $range.data("ionRangeSlider");
		    slider.update({
		        from: 60
		    });
		    slrdObj.setValue( 60 );
		});
		$("button#slrdb_bright").on("click", function () {
			var $range = $("#slrd_slider");
			var slider = $range.data("ionRangeSlider");
		    slider.update({
		        from: 100
		    });
		    slrdObj.setValue( 99 );
		});
		$("button#slrdb_plus").on("click", function () {
			var $range = $("#slrd_slider");
			var slider = $range.data("ionRangeSlider");
			var nv = Math.min(slider.result.from + 10, 100);
		    slider.update({
		        from: nv
		    });
		    slrdObj.setValue( nv );
		});
		$("button#slrdb_min").on("click", function () {
			var $range = $("#slrd_slider");
			var slider = $range.data("ionRangeSlider");
			var nv = Math.max(slider.result.from - 10, 0);
		    slider.update({
		        from: nv
		    });
		    slrdObj.setValue( nv );
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
			    slrdObj.setValue( data.from, false );
	        },
	        onFinish: function (data) {
	        	console.log( timestamp() + ' ---> Slider Livingroom finished on ' + data.from);
//				CentralHSUpdater.notify( hsDev );
	        },
	        onUpdate: function (data) {
				console.log( timestamp() + ' ---> Slider Livingroom updated');
	        }
	    });
		// Register for updates. Bind the callback to this object
		var obj = this;
		CentralHSUpdater.register( 298, function() { obj.draw() } );
		CentralHSUpdater.register( 377, function() { obj.draw() } );
		CentralHSUpdater.register( 422, function() { obj.draw() } );
		CentralHSUpdater.register( 738, function() { obj.draw() } );
		CentralHSUpdater.register( 441, function() { obj.draw() } );
		CentralHSUpdater.register( 508, function() { obj.draw() } );
	}

}

SplashLivingroomDevice.prototype.setValue = function( value, notify = true ) {
	var hsd298 = HSDeviceFactory.create( 598 );						// Buislamp
	hsd298.setValue( value );
	ThrottleSplashHSDeviceUpdate( 298, value );
	if ( notify ) { CentralHSUpdater.notify( HSDeviceFactory.create( 298 ) ); }
	var hsd377 = HSDeviceFactory.create( 377 );						// Touchlamp
	hsd377.setValue( ( value > 10 ? 255 : 0 ) );
	ThrottleSplashHSDeviceUpdate( 377, ( value > 10 ? 255 : 0 ) );
	if ( notify ) { CentralHSUpdater.notify( HSDeviceFactory.create( 377 ) ); }
	var hsd422 = HSDeviceFactory.create( 422 );						// Tripodlamp
	hsd422.setValue( value );
	ThrottleSplashHSDeviceUpdate( 422, value );
	if ( notify ) { CentralHSUpdater.notify( HSDeviceFactory.create( 422 ) ); }
	var hsd738 = HSDeviceFactory.create( 738 );						// Vlechtlamp
	hsd738.setValue( ( value > 20 ? 255 : 0 ) );
	ThrottleSplashHSDeviceUpdate( 738, ( value > 20 ? 255 : 0 ) );
	if ( notify ) { CentralHSUpdater.notify( HSDeviceFactory.create( 738 ) ); }
	var hsd441 = HSDeviceFactory.create( 441 );						// Keuken plafondspots
	hsd441.setValue( value );
	ThrottleSplashHSDeviceUpdate( 441, value );
	if ( notify ) { CentralHSUpdater.notify( HSDeviceFactory.create( 441 ) ); }
	var hsd508 = HSDeviceFactory.create( 508 );						// Gang designlamp
	hsd508.setValue( ( value == 99 ? 99 : ( value < 60 ? ( value == 0 ? 0 : 5 ) : 10 ) ) );
	ThrottleSplashHSDeviceUpdate( 508, ( value == 99 ? 99 : ( value < 60 ? ( value == 0 ? 0 : 5 ) : 10 ) ) );
	if ( notify ) { CentralHSUpdater.notify( HSDeviceFactory.create( 508 ) ); }
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
		$('p#std_' + ref + '_location').slideToggle();	// default slideup
		$('div#std_'+ref).click( function(e) {
			$('p#std_' + ref + '_location').slideToggle();	// slideUp/ slideDown
		});	

		// Register for updates. Bind the callback to this object
		var obj = this;
		CentralHSUpdater.register( ref, function() { obj.draw() } );
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
		$('p#shd_' + ref + '_location').slideToggle();	// default slideup
		$('div#shd_'+ref).click( function(e) {
			$('p#shd_' + ref + '_location').slideToggle();	// slideUp/ slideDown
		});	

		// Register for updates. Bind the callback to this object
		var obj = this;
		CentralHSUpdater.register( ref, function() { obj.draw() } );
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
		$('p#sud_' + ref + '_uptime').slideToggle();	// default slideup
		$('p#sud_' + ref + '_location').slideToggle();	// default slideup
		$('div#sud_'+ref).click( function(e) {
			$('p#sud_' + ref + '_uptime').slideToggle();	// slideUp/ slideDown
			$('p#sud_' + ref + '_location').slideToggle();	// slideUp/ slideDown
			$('p#sud_' + ref + '_location2').slideToggle();	// slideUp/ slideDown
		});	

		// Register for updates. Bind the callback to this object
		var obj = this;
		CentralHSUpdater.register( ref, function() { obj.draw() } );
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
		CentralHSUpdater.register( refLow, function() { obj.draw() } );
		CentralHSUpdater.register( refHigh, function() { obj.draw() } );
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
				CentralHSUpdater.notify( hsDevLow );
				CentralHSUpdater.notify( hsDevHigh );
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
			if ( hsDev.isOff() ) {
            	// Off
            	var el = $('div#sld_'+ref+' div div.bg-icon-warning');
            	el.removeClass('bg-icon-warning');
            	el.addClass('bg-icon-inverse');
            	el = el.find('i.mdi-lightbulb');
            	el.removeClass('mdi-lightbulb');
            	el.addClass('mdi-lightbulb-outline');
            	// Uncheck the switch
            	$('input#sld_'+ref+'_onoff').prop('checked', false);
            } else {
            	// On
            	var el = $('div#sld_'+ref+' div div.bg-icon-inverse');
            	el.removeClass('bg-icon-inverse');
            	el.addClass('bg-icon-warning');
            	el = el.find('i.mdi-lightbulb-outline');
            	el.removeClass('mdi-lightbulb-outline');
            	el.addClass('mdi-lightbulb');
            	// Check the switch
            	$('input#sld_'+ref+'_onoff').prop('checked', true);
            }
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
	        $( this.getBindingElement() ).append('<div class="col-lg-3 col-md-6" id="sld_'+ref+'"><div class="widget-simple-chart text-right card-box"><div id="sld_'+ref+'_circliful" class="circliful-chart" data-dimension="90" data-text="--%" data-width="5" data-fontsize="14" data-percent="100" data-fgcolor="'+CIRCLIFUL_COLOR_GRAY+'" data-bgcolor="'+CIRCLIFUL_COLOR_BG_GRAY+'"></div><div id="sld_'+ref+'_textbox" class="wid-icon-info text-right"><p id="sld_'+ref+'_name" class="text-muted m-b-5 font-13 text-uppercase">---</p><p id="sld_'+ref+'_func" class="text-muted m-b-5 font-15">---</p><h5 class="m-t-0 m-b-5 font-bold"><span id="sld_'+ref+'_location">---</span></h5></div></div></div>');
		} else {
			// Draw regular light
			console.log( timestamp() + " SplashLightDevice.drawElement() - Drawing new Switch element");
	        $( this.getBindingElement() ).append('<div class="col-lg-3 col-md-6" id="sld_'+ref+'"><div class="widget-bg-color-icon card-box"><div class="bg-icon '+(hsDev.isOff()?'bg-icon-inverse':'bg-icon-warning')+' pull-left"><i class="mdi '+(hsDev.isOff()?'mdi-lightbulb-outline':'mdi-lightbulb')+' text-purple"></i></div><div id="sld_'+ref+'_textbox" class="wid-icon-info text-right"><p id="sld_'+ref+'_name" class="text-muted m-b-5 font-13 text-uppercase">---</p><p id="sld_'+ref+'_func" class="text-muted m-b-5 font-15">---</p><h5 class="m-t-0 m-b-5 font-bold"><span id="sld_'+ref+'_location">---</span></h5></div></div></div>');
		}
		// Register for updates. Bind the callback to this object
		var obj = this;
		CentralHSUpdater.register( ref, function() { obj.draw() } );
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
				CentralHSUpdater.notify( hsDev );
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
			if ( $(this).is(":checked") ) {
            	// On
            	var el = $('div#sld_'+ref+' div div.bg-icon-inverse');
            	el.removeClass('bg-icon-inverse');
            	el.addClass('bg-icon-warning');
            	el = el.find('i.mdi-lightbulb-outline');
            	el.removeClass('mdi-lightbulb-outline');
            	el.addClass('mdi-lightbulb');
				hsDev.setValue( 255 );
				ThrottleSplashHSDeviceUpdate( ref, 255 );
            } else {
            	// Off
            	var el = $('div#sld_'+ref+' div div.bg-icon-warning');
            	el.removeClass('bg-icon-warning');
            	el.addClass('bg-icon-inverse');
            	el = el.find('i.mdi-lightbulb');
            	el.removeClass('mdi-lightbulb');
            	el.addClass('mdi-lightbulb-outline');
				hsDev.setValue( 0 );
				ThrottleSplashHSDeviceUpdate( ref, 0 );
            }
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
				CentralHSUpdater.notify( hsDev );
	        },
	        onUpdate: function (data) {
				console.log( timestamp() + ' ---> Slider ' + ref + ' updated');
	        }
	    });

		// Register for updates. Bind the callback to this object
		var obj = this;
		CentralHSUpdater.register( ref, function() { obj.draw() } );
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
		CentralNRUpdater.update( data.serial );
	})
	.fail(function( jqxhr, textStatus, error ) {
		console.log( timestamp() + " SplashNRRobotUpdate() - Error send action to Neato robot. " + textStatus + ", " + error );
		$.Notification.notify('error','top left', 'Connection error', 'Could not send action to from Neato Robotics!' );
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