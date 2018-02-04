// JavaScript Document
console.log("starting script");

//var alfr3d_blue = 0x33b5e5;
//var alfr3d_black = 0x071a21;

// instanciate firebase
var myFirebaseRef = new Firebase("https://alfr3d.firebaseio.com/");

get_users();

function get_users() {
	fetch("http://10.0.0.230:8080/whosthere")
		.then(response => {console.log(response)});
}