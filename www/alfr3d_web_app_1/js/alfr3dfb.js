console.log("loading alfr3dfb.js");

var myFirebaseRef = new Firebase("https://alfr3d.firebaseio.com/");

//replaces all data
// myFirebaseRef.set({
//   title: "Alfr3d Sandbox",
//   author: "Armageddion",
//   location: {
//     city: "Philadelphia",
//     state: "Pennsylvania",
//     zip: 19130
//   }
// });

//adds data
// myFirebaseRef.update({
//   users: {
//     armageddion: {
//     	name: "Armageddion",
//     	location: "Malvern"
//     }
//   }
// });

//password reset
// myFirebaseRef.changePassword({
//   email       : "armageddion@gmail.com",
//   oldPassword : "HNvHN2vhh7MPBaNF",
//   newPassword : "spaske"
// }, function(error) {
//   if (error === null) {
//     console.log("Password changed successfully");
//   } else {
//     console.log("Error changing password:", error);
//   }
// });