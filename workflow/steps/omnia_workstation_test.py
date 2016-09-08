import omnia

WORKFLOW = [
    omnia.PowerTest(),
    omnia.Mcu(),
    omnia.Uboot(),
    omnia.EepromFlash(),
    omnia.UsbFlashClock(),
    #omnia.UbootCommands("USB FLASHING", ["setenv rescue 3", "run rescueboot"], bootPlan=[
    #    ('Router Turris successfully started.', 100),
    #    ('Mode: Reflash...', 50),
    #    ('Reflash succeeded.', 75),
    #]),
    #omnia.ClockSet(),
    omnia.RsvTest(),
]

if omnia.settings.RERUN > 0:
    # rerun enabled
    WORKFLOW = WORKFLOW * omnia.settings.RERUN
