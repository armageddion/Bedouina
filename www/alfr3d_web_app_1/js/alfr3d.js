console.log("loading alfr3d.js");

/***************************************
 *				LOGIN STUFF 
 ***************************************/

// instanciate firebase
var myFirebaseRef = new Firebase("https://alfr3d.firebaseio.com/");

window.onkeydown = function (e) {
    var code = e.keyCode ? e.keyCode : e.which;
    if (code === 27) { //esc key
        alert('There is no way out');
    } else if (code === 13) { //enter key

		myFirebaseRef.authWithPassword({
			email    : document.getElementById('user_id').value,
			password : document.getElementById('pass_wd').value
		}, function(error, authData) {
			if (error) {
				console.log("Login Failed!", error);
				deny();
			} else {
				console.log("Authenticated successfully with payload:", authData);
				login(authData.password.email.replace(/@.*/, ''));
			}
		})
	}
};

var deny = function() {
	console.log("DENIED")
	document.getElementById('section').style.display = 'none';

	img.src = '../img/denied.png';	
	img.onload = function() {
		init();
		window.onresize = init;
	};
};

var login = function(user_id) {
	document.getElementById('section').style.display = 'none';
	myFirebaseRef.child("users/"+user_id+"/name").once('value', function(snapshot) {
		var name = snapshot.val();
		console.log("Welcome back "+name);
	});		
};

/***************************************
 *	 			GLITCH STUFF 
 ***************************************/

// ready canvas for glitch
var canvas = document.getElementById('canvas')
  , context = canvas.getContext('2d')
  , img = new Image()
  , w
  , h
  , offset
  , glitchInterval;

var init = function() {
	clearInterval(glitchInterval);
	canvas.width = w = window.innerWidth;
	offset = w * .1;
	canvas.height = h = img.height;
	glitchInterval = setInterval(function() {
		clear();
		//context.drawImage(img, window.innerWidth/2-img.width/2, 0);
		setTimeout(glitchImg, randInt(250, 1000));
		setTimeout(cleanImg, randInt(500, 1000));
	}, 500);
};

var clear = function() {
	context.rect(0, 0, w, h);
	//context.fill();
	context.clearRect ( 0 , 0 , canvas.width, canvas.height );
};
    
var glitchImg = function() {
	for (var i = 0; i < randInt(1, 13); i++) {
		var x = Math.random() * w;
		var y = Math.random() * h;
		var spliceWidth = w - x;
		var spliceHeight = randInt(5, h / 3);
		context.drawImage(img, 0, y, spliceWidth, spliceHeight, x, y, spliceWidth, spliceHeight);
		context.drawImage(img, spliceWidth, y, x, spliceHeight, 0, y, x, spliceHeight);
	}
};

var cleanImg = function() {
	context.drawImage(img, window.innerWidth/2-img.width/2, 0);
};

var randInt = function(a, b) {
	return ~~(Math.random() * (b - a) + a);
};

// // Tests to see if /users/<userId> has any data. 
// function checkIfUserExists(userId) {
// 	console.log('existance check...');
// 	var exists;
// 	myFirebaseRef.child("users/"+userId).once('value', function(snapshot) {
// 		exists = (snapshot.val() !== null);
// 		console.log("user exists:"+exists);
// 		userExistsCallback(userId, exists);
// 	});	
// };

// function userExistsCallback(userId, exists) {
// 	if (exists) {
// 		console.log("welcome back");
// 	} else {
// 		deny();
// 	}
// }

