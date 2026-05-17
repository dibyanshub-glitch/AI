$(document).ready(function () {
    $('.text').textillate({
        loop: true,
        sync: true,
        in: { effect: "bounceIn" },
        out: { effect: "bounceOut" }
    });

    // siri wave setup
    var siriWave = new SiriWave({
        container: document.getElementById("siri-container"),
        width: 800,
        height: 200,
        style: "ios9",
        amplitude: "1",
        autostart: true
    });



    // siri message animation
    $('.siri-message').textillate({
        loop: true,
        sync: true,
        in: { effect: "fadeInUp", sync: true },
        out: { effect: "fadeOutUp", sync: true }
    });

    // mic button click handler
    $("#MicBtn").click(function (e) {
        eel.playAssistantSound();
        $("#Oval").attr("hidden", true);
        $("#SiriWave").attr("hidden", false);

        eel.allCommands()(function (command) {
            console.log("User said:", command);
            if (command) {
                $(".siri-message").text(command);
            } else {
                console.log("No voice input detected.");
            }
        });
    });


    function doc_keyUp(e) {

        // this would test for whichever key is 40 (down arrow)and the ctrl key at the same time
        if (e.key == 'j' && e.metaKey) {
            eel.playAssistantSound()
            $("#Oval").attr("hidden", true);
            $("#SiriWave").attr("hidden", false);
            eel.allCommands()()
        }
    }
    document.addEventListener('keyup', doc_keyUp, false);

    // Optional: auto start mic
    // $("#MicBtn").click();
});
