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

$("#launch-time").sevenSeg({
    value:"0.0", 
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

async function testIndicators() {
    await sleep(1000);
    $("#master-power-indicator").addClass("active");
    await sleep(1000);
    $("#gse1-indicator").addClass("active");
    await sleep(1000);
    $("#gse2-indicator").addClass("active");
    await sleep(1000);
    $("#teRa-indicator").addClass("active");
    await sleep(1000);
    $("#teRb-indicator").addClass("active");
    await sleep(1000);
    $("#te1-indicator").addClass("active");
    await sleep(1000);
    $("#te2-indicator").addClass("active");
    await sleep(1000);
    $("#te3-indicator").addClass("active");
}

testIndicators();

// Enable/disable manual control
document.getElementById("enable-manual-control").addEventListener("change", (event) => {
    // Check if it is checked
    const enabled = event.currentTarget.checked;
    // Enable or disable based on the checkbox input
    document.getElementById("manual-control-buttons").className = enabled ? "" : "disabled";
});

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
