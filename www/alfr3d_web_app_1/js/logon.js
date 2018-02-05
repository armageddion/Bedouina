console.log("loading logon.js");

// mask url
//window.top.location.href = "http://www.example.com";

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

		// move logo to upper right
		console.log("Shifting the logo")
		document.getElementById('logo').style.animation = "logo_shift 4s";
		document.getElementById('logo').style.right = "10%";
		document.getElementById('logo').style.top = "10%";		

		console.log("Writing URL")
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
				//window.location.href = "http://"+snapshot.val()+"/main.html";
				drawUI();
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

function drawUI() {		
	console.log("Loading UI elements")

	console.log("Hiding login forms")
	document.getElementById('section').style.animation = 'fadeout 3s';	
	document.getElementById('section').style.display = 'none';	

	// add element for window1
	var win1div = document.createElement("div");
	win1div.setAttribute("id", "window1");
	win1div.setAttribute("class", "window1");
	win1div.style.animation = "fadein 3s";
	
	var win1p = document.createElement("p");
	win1p.setAttribute("class", "window_title");
	win1p.appendChild(document.createTextNode("users"));

	var win1p2 = document.createElement("p");
	win1p2.setAttribute("id", "user_data");
	win1p2.setAttribute("class", "window_data");
	win1p2.appendChild(document.createTextNode("<user names>"));
	

	win1div.appendChild(win1p);
	win1div.appendChild(win1p2);
	document.body.insertBefore(win1div,document.getElementById("footer"));

	fetch_user_data();
};

function fetch_user_data() {
	fetch("http://localhost:8080/whosthere", {})
		.then(response => response.json())
		.then(data => {
			console.log("data received:")
			console.log(data)
			if (data.users == 0) {
				document.getElementById("user_data").innerHTML = "no users";
			}
			else {
				content = ""
				for (i=0; i<data.users.length; i++){
					content = content + data.users[i]+"<br>"
				}
				document.getElementById("user_data").innerHTML = content;

			}


		});	

};
