let micLocked = false;
$(document).ready(function () {

    eel.init()()

    $('.text').textillate({
        loop: true,
        sync: true,
        in: {
            effect: "bounceIn",
        },
        out: {
            effect: "bounceOut",
        },

    });

    // Siri configuration
    // var siriWave = new SiriWave({
    //     container: document.getElementById("siri-container"),
    //     width: 800,
    //     height: 200,
    //     style: "ios9",
    //     amplitude: "1",
    //     speed: "0.30",
    //     autostart: true
    //   });

    // Siri message animation
    // $('.siri-message').textillate({
    //     loop: true,
    //     sync: true,
    //     in: {
    //         effect: "fadeInUp",
    //         sync: true,
    //     },
    //     out: {
    //         effect: "fadeOutUp",
    //         sync: true,
    //     },

    // });

    // mic button click event

    $("#MicBtn").click(function () {

        console.log("🎤 MIC BUTTON CLICKED");

        // hide oval
        $("#Oval").attr("hidden", true);

        // show orb safely
        $("#orb-container")
            .css("display", "flex")
            .hide()
            .fadeIn(200);

        // start orb if available
        if (window.lukasOrbStart) {
            window.lukasOrbStart();
        } else {
            console.warn("⚠️ Orb not loaded");
            $("#Oval").attr("hidden", false); // fallback
        }

        try {
            eel.startListening()();
            // eel.startVoiceUI()();
        } catch (e) {
            console.error("Eel call failed:", e);
        }

    });





    function doc_keyUp(e) {
        // this would test for whichever key is 40 (down arrow) and the ctrl key at the same time

        if (e.key === 'j' && e.metaKey) {
            eel.playAssistantSound()
            $("#Oval").attr("hidden", true);
            $("#SiriWave").attr("hidden", false);
            eel.allCommands()()
        }
    }
    document.addEventListener('keyup', doc_keyUp, false);

    // to play assisatnt 
    function PlayAssistant(message) {

        if (message != "") {

            $("#Oval").attr("hidden", true);
            $("#SiriWave").attr("hidden", false);
            eel.allCommands(message)();

            $("#chatbox").val("")
            $("#MicBtn").attr('hidden', false);
            $("#SendBtn").attr('hidden', true);

        }

    }

    // toogle fucntion to hide and display mic and send button 
    function ShowHideButton(message) {
        if (message.length == 0) {
            $("#MicBtn").attr('hidden', false);
            $("#SendBtn").attr('hidden', true);
        }
        else {
            $("#MicBtn").attr('hidden', true);
            $("#SendBtn").attr('hidden', false);
        }
    }

    // key up event handler on text box
    $("#chatbox").keyup(function () {

        let message = $("#chatbox").val();
        ShowHideButton(message)

    });

    // send button event handler
    $("#SendBtn").click(function () {

        let message = $("#chatbox").val()
        PlayAssistant(message)

    });


    // enter press event handler on chat box
    $("#chatbox").keypress(function (e) {
        key = e.which;
        if (key == 13) {
            let message = $("#chatbox").val()
            PlayAssistant(message)
        }
    });




});

// ⚙️ SETTINGS TOGGLE
// ================= SETTINGS TOGGLE =================
// ================= SETTINGS TOGGLE =================

$(document).ready(function () {

    $("#SettingsBtn").click(function () {
        $("#settings-panel").addClass("open");
        $("#settings-backdrop").addClass("show");
    });

    $("#closeSettings, #settings-backdrop").click(function () {
        $("#settings-panel").removeClass("open");
        $("#settings-backdrop").removeClass("show");
    });

});

// ================= TOAST SYSTEM =================

function showToast(message) {
    const toast = document.getElementById("lukas-toast");
    toast.innerText = message;
    toast.classList.add("show");

    setTimeout(() => {
        toast.classList.remove("show");
    }, 2500);
}

// ================= SETTINGS ACTIONS =================

window.lukasSettings = {

    async setVoice(type) {
        await eel.setVoice(type)();
        showToast("Voice switched to " + type);
    },

    async logout() {
        await eel.lukasLogout()();
        location.reload();
    }
};

// ================= CHAT =================

async function startNewChat() {
    await eel.newChat()();
    document.getElementById("chat-canvas-body").innerHTML = "";
    showToast("New chat started");
}

async function exportChat() {
    const data = await eel.exportChat()();
    const blob = new Blob([data], { type: "application/json" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "lukas_chat.json";
    a.click();

    showToast("Chat exported");
}

// ================= SUBSCRIPTION =================

async function lukasUpgrade() {
    const current = await eel.getSubscription()();

    if (current.plan === "pro") {
        showToast("Already using Lukas Pro");
        return;
    }

    await eel.upgradePlan("pro")();
    showToast("Lukas Pro activated");
}

// ================= CONTACT =================

async function openContact() {
    showToast(`
Lukas AI Support

Email: support@lukasai.com
Phone: +91 9876543210
Website: www.lukasai.com
Address: Surat, Gujarat, India

We respond within 24 hours.
    `);
}

// ================= ABOUT =================    
async function openAbout() {
    showToast(`
Lukas AI v1.0.0

Developed by Ankit Kumar
Location: India

Lukas AI is an advanced neural desktop assistant 
powered by local AI models, voice automation, 
and real-time search intelligence.

© 2026 Lukas Neural Systems
    `);
}

document.addEventListener("DOMContentLoaded", function () {

    const toggle = document.getElementById("togglePassword");
    const password = document.getElementById("loginPassword");

    toggle.addEventListener("click", function () {
        const type = password.getAttribute("type") === "password" ? "text" : "password";
        password.setAttribute("type", type);

        this.classList.toggle("bi-eye");
        this.classList.toggle("bi-eye-slash");
    });

});
// ================= LOGIN =================

async function doLogin() {
    const email = document.getElementById("loginEmail").value;
    const pass = document.getElementById("loginPassword").value;

    const response = await eel.lukasLogin(email, pass)();

    if (response.success) {
        document.getElementById("login-screen").style.display = "none";
        showToast("🔥 Welcome Commander");
    } else {
        showToast("❌ " + response.message);
    }
}

async function doRegister() {
    const email = document.getElementById("loginEmail").value;
    const pass = document.getElementById("loginPassword").value;

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailRegex.test(email)) {
        showToast("❌ Invalid email format");
        return;
    }

    if (pass.length < 6) {
        showToast("⚠️ Password must be at least 6 characters");
        return;
    }

    const response = await eel.lukasRegister(email, pass)();

    if (response.ok) {
        showToast("✅ Registered successfully");
    } else {
        showToast("⚠️ " + response.msg);
    }
}

async function continueGuest() {
    const res = await eel.guestLogin()();
    if (res.success) {
        document.getElementById("login-screen").style.display = "none";
        showToast("Guest mode enabled");
    }
}

