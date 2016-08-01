import omnia

WORKFLOW = [
    omnia.PowerTest(),
    omnia.Mcu(),
    omnia.Uboot(),
    omnia.EepromFlash(),
    omnia.UsbFlashClockRsv(),
    #omnia.UbootCommands("USB FLASHING", ["setenv rescue 3", "run rescueboot"], bootPlan=[
    #    ('Router Turris successfully started.', 100),
    #    ('Mode: Reflash...', 50),
    #    ('Reflash succeeded.', 75),
    #]),
    #omnia.ClockSet(),
    #omnia.RsvTest(),
]

# continue on error
for step in WORKFLOW:
    step.continueOnFailure = True
