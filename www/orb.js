// ======================================
// 🎤 VOICE ENERGY (GLOBAL)
// ======================================
let manualClosed = false;
let emotionPhase = 0;
let emotionIntensity = 0;
let breathPhase = 0;
let breathSpeed = 0.0025; // breathing speed
let autoVoiceStarted = false;
let micStream = null;
lastVoiceTime = Date.now();
const SILENCE_TIMEOUT = 15000;
let voiceEnergy = 0;

window.updateVoiceEnergy = function (level) {
    voiceEnergy = Math.min(Math.max(level, 0), 1);
    // lastVoiceTime = Date.now(); // Update last voice time when energy is updated

};
// ======================================
// 🔇 ASSISTANT SPEECH LOCK
// ======================================

let assistantSpeaking = false;

window.lukasSetSpeaking = function (state) {
    assistantSpeaking = state;
};

// =====================================================
// 👑 LUKAS FINAL FORM ORB
// =====================================================

let orbCanvas, orbCtx;
let audioCtx, analyser, dataArray;
let animationId;
let isOrbRunning = false;

let particles = [];
let energy = 0;
let speaking = false;
let silenceTimer = 0;
let ringRotation = 0;
let ringPulse = 0;

// 🎨 STATES
const COLORS = {
    idle: 190,       // cyan
    listening: 210,  // blue
    speaking: 280,   // purple
    thinking: 45     // gold
};

let currentHue = COLORS.idle;
const IDLE_SCALE = 0.78;
const MAX_SCALE = 1.65;

// =====================================================
// ✨ PARTICLES
// =====================================================

function createParticles(count) {
    particles = [];
    for (let i = 0; i < count; i++) {
        particles.push({
            angle: Math.random() * Math.PI * 2,
            radius: 95 + Math.random() * 40,
            speed: 0.002 + Math.random() * 0.004,
            size: 1 + Math.random() * 2,
        });
    }
}

function drawParticles(volume, cx, cy) {
    particles.forEach(p => {
        p.angle += p.speed * (1 + volume * 6);

        const x = cx + Math.cos(p.angle) * p.radius;
        const y = cy + Math.sin(p.angle) * p.radius;

        orbCtx.beginPath();
        orbCtx.arc(x, y, p.size + volume * 2.2, 0, Math.PI * 2);
        orbCtx.fillStyle = `hsla(${currentHue},100%,65%,${0.25 + volume * 0.6})`;
        orbCtx.fill();
    });
}

// =====================================================
// 🌊 LIQUID CORE
// =====================================================

function drawCore(volume, cx, cy, baseRadius) {
    const points = 72;
    orbCtx.beginPath();

    for (let i = 0; i <= points; i++) {
        const angle = (i / points) * Math.PI * 2;

        const wave =
            Math.sin(Date.now() * 0.004 + i) *
            (4 + volume * 20);

        const r = baseRadius + wave;

        const x = cx + Math.cos(angle) * r;
        const y = cy + Math.sin(angle) * r;

        if (i === 0) orbCtx.moveTo(x, y);
        else orbCtx.lineTo(x, y);
    }

    const grad = orbCtx.createRadialGradient(
        cx, cy, baseRadius * 0.2,
        cx, cy, baseRadius * 2.5
    );

    grad.addColorStop(0, `hsla(${currentHue},100%,70%,0.95)`);
    grad.addColorStop(0.4, `hsla(${currentHue + 20},100%,55%,0.55)`);
    grad.addColorStop(1, `hsla(${currentHue + 40},100%,40%,0.05)`);

    orbCtx.fillStyle = grad;
    orbCtx.fill();
}

// =====================================================
// 🎵 WAVE RING
// =====================================================

function drawWaveRing(volume, cx, cy, baseRadius) {
    const bars = 64;

    for (let i = 0; i < bars; i++) {
        const angle = (i / bars) * Math.PI * 2;

        const bar = analyser
            ? dataArray[i % dataArray.length] / 255
            : volume;

        const length = 8 + bar * 50;

        const x1 = cx + Math.cos(angle) * (baseRadius + 35);
        const y1 = cy + Math.sin(angle) * (baseRadius + 35);

        const x2 = cx + Math.cos(angle) * (baseRadius + 35 + length);
        const y2 = cy + Math.sin(angle) * (baseRadius + 35 + length);

        orbCtx.beginPath();
        orbCtx.moveTo(x1, y1);
        orbCtx.lineTo(x2, y2);
        orbCtx.strokeStyle = `hsla(${currentHue},100%,65%,${0.25 + volume})`;
        orbCtx.lineWidth = 2;
        orbCtx.stroke();
    }
}
// =====================================================
// 🌀 DOCTOR STRANGE MYSTIC RINGS
// =====================================================
function drawMysticRings(volume, cx, cy, baseRadius) {
    ringRotation += 0.01 + volume * 0.05;
    ringPulse += 0.04;

    const rings = 3;

    for (let r = 0; r < rings; r++) {
        const radius = baseRadius + 80 + r * 26;

        orbCtx.beginPath();

        for (let i = 0; i <= 120; i++) {
            const angle =
                (i / 120) * Math.PI * 2 +
                ringRotation * (r % 2 ? 1 : -1);

            const warp =
                Math.sin(angle * 6 + ringPulse) *
                (4 + volume * 12);

            const rr = radius + warp;

            const x = cx + Math.cos(angle) * rr;
            const y = cy + Math.sin(angle) * rr;

            if (i === 0) orbCtx.moveTo(x, y);
            else orbCtx.lineTo(x, y);
        }

        orbCtx.strokeStyle =
            `hsla(${currentHue + r * 25},100%,65%,${0.25 + volume * 0.5})`;

        orbCtx.lineWidth = 1.5 + volume * 2;
        orbCtx.stroke();
    }
}
// =====================================================
// 🧠 SPEECH DETECTOR (MAGIC)
// =====================================================

function detectSpeech(volume) {
    if (volume > 0.12) {
        speaking = true;
        silenceTimer = 0;
        currentHue = COLORS.speaking;
    } else {
        silenceTimer++;

        if (silenceTimer > 25) {
            speaking = false;
            currentHue = COLORS.idle;
        }
    }
}

// =====================================================
// 🎨 MAIN DRAW
// =====================================================

function drawOrb(volume) {
    const w = orbCanvas.width;
    const h = orbCanvas.height;

    orbCtx.clearRect(0, 0, w, h);
    // ======================================
    // 🔥 ULTRA REACTIVE SCALE (FIXED)
    // ======================================
    // 🔥 SAFE — do NOT move canvas origin
    orbCtx.setTransform(1, 0, 0, 1, 0, 0);

    const cx = w / 2;
    const cy = h / 2;
    const baseRadius = 65;

    energy += (volume - energy) * 0.15;

    detectSpeech(energy);
    /* ===============================
       🧠 EMOTION ENGINE
    ================================ */

    emotionIntensity += (energy - emotionIntensity) * 0.08;
    emotionPhase += 0.04;

    const emotionPulse =
        Math.sin(emotionPhase) * (0.03 + emotionIntensity * 0.06);

    emotionPulse;
    // 🔥 ULTRA SCALE
    // 🫁 NEURAL BREATHING ENGINE
    breathPhase += breathSpeed;

    const breathing =
        Math.sin(breathPhase) * 0.035; // gentle life motion

    const orbscale =
        IDLE_SCALE +
        energy * (MAX_SCALE - IDLE_SCALE) +
        breathing + emotionPulse;

    orbCanvas.style.transform = `scale(${orbscale})`;

    // 🎭 transparency intelligence
    orbCanvas.style.opacity = 0.75 + energy * 0.35;

    drawMysticRings(energy, cx, cy, baseRadius);
    drawCore(energy, cx, cy, baseRadius);
    drawWaveRing(energy, cx, cy, baseRadius);
    drawParticles(energy, cx, cy);
}

// =====================================================
// 🎤 LOOP
// =====================================================

function animateOrb() {
    if (!isOrbRunning) return;

    analyser.getByteFrequencyData(dataArray);

    let sum = 0;
    for (let i = 0; i < dataArray.length; i++) sum += dataArray[i];

    const volumeRaw = Math.min(sum / dataArray.length / 128, 1);

    // 🚫 ignore mic while assistant speaking
    let volume = volumeRaw;

    // 🚫 HARD BLOCK while assistant speaking
    if (assistantSpeaking) {
        volume = 0;
        energy *= 0.85; // smooth decay
    }

    // only update lastVoiceTime for REAL user speech
    if (!assistantSpeaking && volume > 0.05) {
        lastVoiceTime = Date.now();
    }
    // 🧠 AUTO WAKE if voice detected while UI hidden
    if (!manualClosed && !isOrbRunning && volume > 0.08) {
        console.log("🎤 Voice auto-wake");

        if (window.eel) {
            try {
                eel.startVoiceUI()();
            } catch (e) {
                console.warn("eel startVoiceUI failed:", e);
            }
        }
    }

    drawOrb(volume);
    // 🧠 AUTO SILENCE CLOSE
    // 🧠 AUTO SILENCE CLOSE (safe version)
    if (isOrbRunning && Date.now() - lastVoiceTime > SILENCE_TIMEOUT) {
        console.log("😴 Silence detected — closing orb");

        isOrbRunning = false;

        if (window.eel) {
            try {
                eel.stopVoiceUI()();
            } catch (e) {
                console.warn("eel stop failed");
            }
        }

        return;
    }

    animationId = requestAnimationFrame(animateOrb);
}

// =====================================================
// 🚀 START
// =====================================================

window.lukasOrbStart = async function () {
    console.log("👑 FINAL FORM ORB START");

    if (isOrbRunning) return;

    orbCanvas = document.getElementById("lukas-orb");
    if (!orbCanvas) {
        console.error("❌ lukas-orb canvas missing");
        return;
    }
    orbCanvas.width = 340;
    orbCanvas.height = 340;
    orbCtx = orbCanvas.getContext("2d");
    createParticles(52);

    try {
        // 🎤 MUST resume audio context on user gesture
        if (!micStream) {
            micStream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });
        }
        const stream = micStream;

        audioCtx = new (window.AudioContext || window.webkitAudioContext)();

        // 🚨 critical fix for suspended context
        if (audioCtx.state === "suspended") {
            await audioCtx.resume();
        }

        analyser = audioCtx.createAnalyser();
        const source = audioCtx.createMediaStreamSource(stream);
        source.connect(analyser);

        analyser.fftSize = 256;
        dataArray = new Uint8Array(analyser.frequencyBinCount);

        lastVoiceTime = Date.now(); // 🔥 IMPORTANT

        isOrbRunning = true;
        animateOrb();

        console.log("✅ Orb running");

    } catch (err) {
        console.error("❌ Mic permission error:", err);
    }
};
// =====================================================
// 🛑 STOP
// =====================================================

window.lukasOrbStop = function () {
    isOrbRunning = false;

    if (animationId) cancelAnimationFrame(animationId);

    if (audioCtx) {
        audioCtx.close();
        audioCtx = null;
    }

    const orb = document.getElementById("lukas-orb");
    if (orb) orb.style.transform = "scale(0.78)";
};

// =====================================================
// ❌ MANUAL CLOSE ORB
// =====================================================
window.lukasOrbManualClose = function () {

    console.log("❌ Orb manually closed");

    manualClosed = true;

    // stop orb
    window.lukasOrbStop();

    // hide UI
    const orb = document.getElementById("orb-container");
    if (orb) orb.style.display = "none";

    // restore main UI
    const oval = document.getElementById("Oval");
    if (oval) oval.hidden = false;

    // stop listening safely
    if (window.eel) {
        try { eel.stopListening()(); } catch {}
    }

    // 🔥 reset auto-wake after 5 sec
    setTimeout(() => {
        manualClosed = false;
        console.log("🔓 Auto-wake re-enabled");
    }, 5000);
};