$(document).ready(function () {



    // Display Speak Message
    eel.expose(DisplayMessage)
    function DisplayMessage(message) {

        $(".siri-message .text li").text(message);
        $('.siri-message').textillate('start');

    }

    // Display hood
    eel.expose(ShowHood)
    function ShowHood() {
        console.log("🏠 Restoring main UI");
        window.micLocked = false;
        // hide orb completely
        $("#orb-container").hide();

        // stop orb engine safely
        if (window.lukasOrbStop) {
            window.lukasOrbStop();
        }

        // restore main UI
        $("#Oval").attr("hidden", false);
    }
    eel.expose(senderText)
    function senderText(message) {
        var chatBox = document.getElementById("chat-canvas-body");
        if (message.trim() !== "") {
            chatBox.innerHTML += `<div class="row justify-content-end mb-4">
            <div class = "width-size">
            <div class="sender_message">${message}</div>
        </div>`;

            // Scroll to the bottom of the chat box
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    }

    eel.expose(receiverText)
    function receiverText(message) {

        var chatBox = document.getElementById("chat-canvas-body");
        if (message.trim() !== "") {
            chatBox.innerHTML += `<div class="row justify-content-start mb-4">
            <div class = "width-size">
            <div class="receiver_message">${message}</div>
            </div>
        </div>`;

            // Scroll to the bottom of the chat box
            chatBox.scrollTo({
                top: chatBox.scrollHeight,
                behavior: "smooth"
            });

        }

    }


    // Hide Loader and display Face Auth animation
    eel.expose(hideLoader)
    function hideLoader() {

        $("#Loader").attr("hidden", true);
        $("#FaceAuth").attr("hidden", false);

    }
    // Hide Face auth and display Face Auth success animation
    eel.expose(hideFaceAuth)
    function hideFaceAuth() {

        $("#FaceAuth").attr("hidden", true);
        $("#FaceAuthSuccess").attr("hidden", false);

    }
    // Hide success and display 
    eel.expose(hideFaceAuthSuccess)
    function hideFaceAuthSuccess() {

        $("#FaceAuthSuccess").attr("hidden", true);
        $("#HelloGreet").attr("hidden", false);

    }


    // Hide Start Page and display blob
    eel.expose(hideStart)
    function hideStart() {

        $("#Start").attr("hidden", true);

        setTimeout(function () {
            $("#Oval").addClass("animate__animated animate__zoomIn");

        }, 1000)
        setTimeout(function () {
            $("#Oval").attr("hidden", false);
        }, 1000)
    }


});

let voiceUIActive = false;

eel.expose(startVoiceUI)
function startVoiceUI() {

    if (voiceUIActive) return;

    voiceUIActive = true;
    window.micLocked = true;

    console.log("🎤 Voice UI START");

    $("#Oval").attr("hidden", true);

    $("#orb-container")
        .stop(true, true)
        .css("display", "flex")
        .hide()
        .fadeIn(180);

    setTimeout(() => {
        if (window.lukasOrbStart) {
            window.lukasOrbStart();
        }
    }, 60);
}
// 🔴 REQUIRED — Python is calling this
eel.expose(stopVoiceUI);
function stopVoiceUI() {

    console.log("🛑 Voice UI STOP");

    voiceUIActive = false;        // ✅ IMPORTANT
    window.micLocked = false;     // ✅ unlock mic

    $("#orb-container").stop(true, true).fadeOut(120, () => {
        $("#Oval").attr("hidden", false);
    });

    if (window.lukasOrbStop) {
        window.lukasOrbStop();
    }
}
// eel.expose(startVoiceUI)
// function startVoiceUI() {
//     console.log("🎤 Voice UI START");

//     // 🛑 prevent double start
//     if ($("#orb-container").is(":visible")) {
//         console.log("⚠️ Orb already visible");
//         return;
//     }

//     // hide oval immediately
//     $("#Oval").attr("hidden", true);

//     // show orb smoothly
//     $("#orb-container")
//         .stop(true, true)
//         .css("display", "flex")
//         .hide()
//         .fadeIn(180);

//     // start orb AFTER visible (very important)
//     setTimeout(() => {
//         if (window.lukasOrbStart) {
//             window.lukasOrbStart();
//         } else {
//             console.warn("⚠️ lukasOrbStart missing");
//         }
//     }, 60);
// }

// ===============================
// ⚙️ SETTINGS ACTIONS
// ===============================

window.lukasSettings = {

    async setVoice(type) {
        await eel.setVoice(type)();
    },

    async logout() {
        await eel.lukasLogout()();
        $("#login-screen").fadeIn(300);
    }
};

$(document).on("click", "#orb-close-btn", function () {
    console.log("❌ CLOSE BUTTON");

    voiceUIActive = false;
    window.micLocked = false;

    if (window.lukasOrbManualClose) {
        window.lukasOrbManualClose();
    }
});