/*
    Payload Control Front End
*/

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

setTimeout(() => {
    setInterval(() => {
        $("#total-power").sevenSeg({
            value:"0.00"
        });
        $("#current-draw").sevenSeg({
            value:"0.00"
        });
    }, 1000)
}, 500)

setInterval(() => {
    $("#total-power").sevenSeg({
        value:"___"
    });
    $("#current-draw").sevenSeg({
        value:"___"
    });
}, 1000);