

  // Your web app's Firebase configuration
 // var firebaseConfig = {
 //   apiKey: "AIzaSyBo2ifIxNa7Cv9Xsg0KLuBg_NVSMrgCh0Y",
 //   authDomain: "form-c16d8.firebaseapp.com",
 //   projectId: "form-c16d8",
 //   storageBucket: "form-c16d8.appspot.com",
 //   messagingSenderId: "891096337791",
 //   appId: "1:891096337791:web:a8239c67063895c30f9e4a"
 // };

 var firebaseConfig = {
    apiKey: "AIzaSyAFBjFieJMgWj09gs6yFxjRgLbAUv5LmPw",
    authDomain: "loginapp-87374.firebaseapp.com",
    projectId: "loginapp-87374",
    storageBucket: "loginapp-87374.appspot.com",
    messagingSenderId: "455049584409",
    appId: "1:455049584409:web:8569fc3a5db2102f446f88",
    measurementId: "G-ZMYCR4BDR1"
  };

  // Initialize Firebase
  firebase.initializeApp(firebaseConfig);

  const auth = firebase.auth();
  
  function signUp(){
	  
	  
	  var email = document.getElementById("email");
	  var password = document.getElementById("password");
	  
	  const promise = auth.createUserWithEmailAndPassword(email.value, password.value);
	  promise.catch(e => alert(e.message));
	  
	  alert("Signed In");
	  
  }

  function signIn(){
		
		var email = document.getElementById("email");
		var password = document.getElementById("password");
		
		const promise = auth.signInWithEmailAndPassword(email.value, password.value);
		promise.catch(e => alert(e.message));
		
		
		// Take a user to a different page or home page
		window.location = "/home"
		
		alert(email);
		
		}
	function signOut(){
		
		auth.signOut();
		alert("Signed Out");
		
	}
	auth.onAuthStateChanged(function(user){
		if(user){
			var email = user.email;
			window.location = "/home"
			//alert("Active User " + email);
			
			//Take user to a different or home 
			//is signed in	
			auth.signOut();
		}else{
			
			//alert("No Active User");
			//no user is signed in
		}
	});
	
function login_google(){
		var provider = new firebase.auth.GoogleAuthProvider();
		provider.addScope('profile')
		provider.addScope('email')
	  
		console.log("executed");
		firebase.auth().signInWithPopup(provider).then(function (result){
			var token = result.credential.accessToken;
			var user = result.user
		});
		
		//console.log(get_userEmail());
		
	  }

	