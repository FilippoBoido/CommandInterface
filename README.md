# Project overview:

Create your own command console interface thanks to the signal and signal analyzer abstract classes.

## Quick help for the Twincat implementation used to fetch ADS-Symbols from a Beckhoff PLC Runtime:

1) When creating notifications with the Notification: or Notification list: signal a new ADSNotification.txt file is created.
2) To ease the live view of the modified ADS Symbol open a powershell on windows and enter: Get-Content -Path "ADSNotification.txt" -Wait

## General help

1) Use the command invoke build-exe to build an exe of the Twincat Command Interface implementation.