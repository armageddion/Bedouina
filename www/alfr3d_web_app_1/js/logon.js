console.log("loading logon.js");

// mask url
window.top.location.href = "http://www.example.com";

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

function deny() {
	console.log("DENIED")
	var den = document.getElementById('pass_wd');
	console.log(den);
	den.value = '';	
	
	//den.style.backgroundImage = "url('../img/SVG/index_password_bad.svg')";
	var changeimg = document.head.appendChild(document.createElement("style"));
	changeimg.innerHTML = ".input:nth-child(2):before {background-image: url('../img/SVG/index_password_bad.svg');}";
};

// Tests to see if /users/<userId> has any data. 
function login(user_id) {
	console.log('existance check...');
	//document.getElementById('section').style.display = 'none';
	myFirebaseRef.child("users/"+user_id+"/name").once('value', function(snapshot) {
		exists = (snapshot.val() !== null);
		console.log("user exists:"+exists);
		userExistsCallback(user_id, exists);
	});		
};

function userExistsCallback(user_id, exists) {
	if (exists) {
		var changeimg = document.head.appendChild(document.createElement("style"));
		changeimg.innerHTML = ".input:nth-child(2):before {background-image: url('../img/SVG/index_password_good.svg');}";		
		welcome(user_id);
 	} else {
 		// Create user
 		new_user(user_id);
 	}
}


/***************************************
 *	 			WELCOME PAGE 
 ***************************************/

 function welcome(user_id) {
	myFirebaseRef.child("users/"+user_id+"/name").once('value', function(snapshot) { 
		var name = snapshot.val();
	});	

	console.log("Welcome back "+name);

	// write alfr3d_url at the top of the page
	myFirebaseRef.child("users/"+user_id+"/location").once('value', function(snapshot) { 		
		console.log('location: '+snapshot.val());

		ref = snapshot.val();
		ret = '';
		ret_counter = 0;

		write();

		function write() {
			var timer = setTimeout(function(){
				ret+=snapshot.val().charAt(ret_counter);
				ret_counter++;
				console.log(ret);
				document.getElementById('alfr3d_url').innerHTML = ret;			
				write();
			}, randInt(100, 300));
			if (ret_counter >= snapshot.val().length) {
				clearTimeout(timer); 
				window.location.href = "http://"+snapshot.val()+"/main.html";
			}
		}
	});	
 };

 function new_user(user_id) {
 	// TO-DO:
 	console.log("Creating new user profile for "+user_id);
 };

var randInt = function(a, b) {
	return ~~(Math.random() * (b - a) + a);
};
