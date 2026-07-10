function openLogin() {
    document.getElementById("loginModal").style.display = "block";
}

function closeLogin() {
    document.getElementById("loginModal").style.display = "none";
}

function checkStaticLogin() {
    const user = document.getElementById("userInput").value;
    const pass = document.getElementById("passInput").value;

    if (user === "coach" && pass === "1234") {
        alert("Welcome Coach!");
        closeLogin();
        window.location.href = "/league/players/";
    } else {
        alert("Incorrect credentials. Try 'coach' & '1234'");
    }
}