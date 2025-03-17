<script type="module">
    // Import the functions you need from the SDKs you need
    import { initializeApp } from "https://www.gstatic.com/firebasejs/11.4.0/firebase-app.js";
    import { getAuth, signInWithEmailAndPassword  } from "https://www.gstatic.com/firebasejs/11.4.0/firebase-auth.js";
    // TODO: Add SDKs for Firebase products that you want to use
    // https://firebase.google.com/docs/web/setup#available-libraries

    // Your web app's Firebase configuration
    const firebaseConfig = {
        apiKey: "AIzaSyD2Ot0EikJNBtrDx9KANvNNS51M1C8MjAI",
        authDomain: "forgineer.firebaseapp.com",
        projectId: "forgineer",
        storageBucket: "forgineer.firebasestorage.app",
        messagingSenderId: "626166887151",
        appId: "1:626166887151:web:e7f7da73df0734d0c9611a"
    };

    // Initialize Firebase
    const app = initializeApp(firebaseConfig);
    const auth = getAuth(app);

    const loginForm = document.getElementById('loginForm');

    loginForm.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent default form submission

        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        signInWithEmailAndPassword(auth, email, password)
        .then((userCredential) => {
            const user = userCredential.user;
            console.log(user);
            console.log(user.getIdToken());
            user.getIdToken().then(function(idToken) {
                // Send the ID token to your Flask backend
                fetch('/login', {
                    method: 'POST',
                    headers: {
                        'Authorization': 'Bearer ' + idToken,
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.message === "Logged in successfully") {
                        alert("Login successful!"); // Or redirect
                        //redirect the user to a new page.
                    } else {
                        alert("Login failed: " + data.error);
                    }
                })
                .catch(error => {
                    alert("Network error: " + error);
                });
            });
        })
        .catch((error) => {
            alert("Firebase Auth error: " + error.message);
        });
    });
</script>