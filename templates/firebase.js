<script type="module">
    // Import the functions you need from the SDKs you need
    import { initializeApp } from "https://www.gstatic.com/firebasejs/11.4.0/firebase-app.js";
    import { getAuth, signInWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/11.4.0/firebase-auth.js";
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

    window.authenticate = function() {
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        return signInWithEmailAndPassword(auth, email, password)
            .then((userCredential) => {
                const user = userCredential.user;
                return user.getIdToken(); // Return the Promise of ID token.
            })
            .catch((error) => {
                console.error("Firebase authentication error:", error);
                throw error; // Propagate the error.
            });
    };

    window.sendAuth = function() {
        window.authenticate().then((idToken)=> {
            htmx.ajax('POST', '{{ url_for("auth.login")}}', {
                values: { idToken: idToken },
                target: '.content', // Specify the target element
                swap: 'innerHTML'   // Specify the swap strategy
            });
        }).catch((error)=>{
            alert(error.message); // display error to user.
        });
    }
</script>