// JavaScript Document
console.log("starting script");

//var alfr3d_blue = 0x33b5e5;
//var alfr3d_black = 0x071a21;

// instanciate firebase
var myFirebaseRef = new Firebase("https://alfr3d.firebaseio.com/");

function get_users() {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", "http:armageddion.no-ip.info/whosthere", false ); // false for synchronous request
    xmlHttp.send( null );
    console.log(xmlHttp.responseText);
};