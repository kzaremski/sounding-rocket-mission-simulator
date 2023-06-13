/*
    Payload Control Front End
*/

// Initialize the 7 segment displays
$("#launch-time").sevenSeg({
    digits:5, 
    colorOff: "#002100", 
    colorOn: "Lime",
    slant: 10
});

$("#current-draw").sevenSeg({
    digits:3, 
    value:"0.00", 
    slant: 10
});

$("#total-power").sevenSeg({
    digits:3, 
    value:"0.00", 
    slant: 10
});

$("#next-timer-event").sevenSeg({
    digits:4,
    value:"0.0",
    colorOff: "#212000", 
    colorOn: "Yellow",
    slant: 10
});


$("#timer-event-dwell").sevenSeg({
    digits:4,
    value:"0.0",
    colorOff: "#212000", 
    colorOn: "Yellow",
    slant: 10
});

/**
 * Sleep within an async function for a certain amount of time.
 * @param {Number} ms - How long to sleep for 
 * @returns Promise for setTimeout which this function wraps.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));

// Until I get the current measurement module installed it will just blink the current measurement displays
async function blinkPower() {
    while (true) {
        $("#total-power").sevenSeg({ value:"___" });
        $("#current-draw").sevenSeg({ value:"___" });
        await sleep(1000);
        $("#total-power").sevenSeg({ value:"0.0" });
        $("#current-draw").sevenSeg({ value:"0.0" });
        await sleep(1000);
    }
}
blinkPower();

// ** Handle displays and indicators
// Create WebSocket connection.
const socket = io();
socket.on('connect', function() {
    setInterval(() => { 
        socket.send('get');
    }, 30);
});
// Each message is a state
socket.on("message", function(message) {
    // Get the response as JSON
    const res = JSON.parse(message);
    // Update the indicators
    res.channels.POWER_SUPPLY_RELAY === 1 ? document.getElementById("master-power-indicator").classList.add("active") : document.getElementById("master-power-indicator").classList.remove("active");
    res.channels.GSE_1_RELAY === 1 ? document.getElementById("gse1-indicator").classList.add("active") : document.getElementById("gse1-indicator").classList.remove("active");
    res.channels.GSE_2_RELAY === 1 ? document.getElementById("gse2-indicator").classList.add("active") : document.getElementById("gse2-indicator").classList.remove("active");
    res.channels.TE_R_A_RELAY === 1 ? document.getElementById("teRa-indicator").classList.add("active") : document.getElementById("teRa-indicator").classList.remove("active");
    res.channels.TE_R_B_RELAY === 1 ? document.getElementById("teRb-indicator").classList.add("active") : document.getElementById("teRb-indicator").classList.remove("active");
    res.channels.TE_1_RELAY === 1 ? document.getElementById("te1-indicator").classList.add("active") : document.getElementById("te1-indicator").classList.remove("active");
    res.channels.TE_2_RELAY === 1 ? document.getElementById("te2-indicator").classList.add("active") : document.getElementById("te2-indicator").classList.remove("active");
    res.channels.TE_3_RELAY === 1 ? document.getElementById("te3-indicator").classList.add("active") : document.getElementById("te3-indicator").classList.remove("active");
    // Update the times
    $("#launch-time").sevenSeg({ value: res.time.launch.toFixed(1) });
    $("#next-timer-event").sevenSeg({ value: res.time.event.toFixed(1) });
    $("#timer-event-dwell").sevenSeg({ value: res.time.dwell.toFixed(1) });

    // Update the manual control buttons
    res.channels.POWER_SUPPLY_RELAY === 1 ? document.getElementById("master-button").classList.add("active") : document.getElementById("master-button").classList.remove("active");
    res.channels.GSE_1_RELAY === 1 ? document.getElementById("gse1-button").classList.add("active") : document.getElementById("gse1-button").classList.remove("active");
    res.channels.GSE_2_RELAY === 1 ? document.getElementById("gse2-button").classList.add("active") : document.getElementById("gse2-button").classList.remove("active");
    res.channels.TE_R_A_RELAY === 1 ? document.getElementById("teRa-button").classList.add("active") : document.getElementById("teRa-button").classList.remove("active");
    res.channels.TE_R_B_RELAY === 1 ? document.getElementById("teRb-button").classList.add("active") : document.getElementById("teRb-button").classList.remove("active");
    res.channels.TE_1_RELAY === 1 ? document.getElementById("te1-button").classList.add("active") : document.getElementById("te1-button").classList.remove("active");
    res.channels.TE_2_RELAY === 1 ? document.getElementById("te2-button").classList.add("active") : document.getElementById("te2-button").classList.remove("active");
    res.channels.TE_3_RELAY === 1 ? document.getElementById("te3-button").classList.add("active") : document.getElementById("te3-button").classList.remove("active");
});

// Enable/disable manual control
document.getElementById("enable-manual-control").addEventListener("change", (event) => {
    // Check if it is checked
    const enabled = event.currentTarget.checked;
    // Enable or disable based on the checkbox input
    document.getElementById("manual-control-buttons").className = enabled ? "" : "disabled";
});

/**
 * Handle the clicking of any manual control button
 */
function handleManualControlButtonClick(event) {
    // Do nothing if manual control not enabled
    if (document.getElementById("manual-control-buttons").className === "disabled") return;
    // Map button against relays
    const relays = {
        "kill-power": "KILL",
        "master-button": "POWER_SUPPLY_RELAY",
        "gse1-button": "GSE_1_RELAY",
        "gse2-button": "GSE_2_RELAY",
        "teRa-button": "TE_R_A_RELAY",
        "teRb-button": "TE_R_B_RELAY",
        "te1-button": "TE_1_RELAY",
        "te2-button": "TE_2_RELAY",
        "te3-button": "TE_3_RELAY",
    }
    const relay = relays[event.currentTarget.id];
    // Toggle
    if (relay === "KILL") {
        document.getElementById("kill-power").classList.add("active");
        setTimeout(() => {
            document.getElementById("kill-power").classList.remove("active");
        }, 500);
    }
    fetch("/api/manual/" + relay)
}
document.getElementById("kill-power").addEventListener("click", handleManualControlButtonClick);
document.getElementById("master-button").addEventListener("click", handleManualControlButtonClick);
document.getElementById("gse1-button").addEventListener("click", handleManualControlButtonClick);
document.getElementById("gse2-button").addEventListener("click", handleManualControlButtonClick);
document.getElementById("teRa-button").addEventListener("click", handleManualControlButtonClick);
document.getElementById("teRb-button").addEventListener("click", handleManualControlButtonClick);
document.getElementById("te1-button").addEventListener("click", handleManualControlButtonClick);
document.getElementById("te2-button").addEventListener("click", handleManualControlButtonClick);
document.getElementById("te3-button").addEventListener("click", handleManualControlButtonClick);

// Populate mission parameters
const timerEvents = [
    "GSE-1",
    "GSE-2",
    "TE-Ra",
    "TE-Rb",
    "TE-1",
    "TE-2",
    "TE-3",
];

const missionParametersTable = document.getElementById("mission-parameters-table");
missionParametersTable.innerHTML = `
    <tr>
        <td>Use?</td>
        <td>Event</td>
        <td>Time</td>
        <td>Dwell</td>
    </tr>
`;
for (timerEvent of timerEvents) {
    missionParametersTable.innerHTML += `
        <tr>
            <td><input type="checkbox" id="${timerEvent}_enabled_checkbox"/></td>
            <td>${timerEvent}</td>
            <td><input type="number" value="0" id="${timerEvent}_time"/></td>
            <td><input type="number" min="1" value="1" id="${timerEvent}_dwell"/></td>
        </tr>
    `;
}
