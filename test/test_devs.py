"""
This is a basic manual test for the Device and DevSwitch classes.
This is currently based on uhubctl for controlling USB hubs.
A YAML file with device definitions of attached devices is required.
Remember that the udev rules must be set properly to allow
non-root access to the USB hubs.
"""
import sys
import time

sys.path.append('..')

from devs import Device, DevSwitch

"""
Provide a YAML file which include one or several devices 
to test the Device and DevSwitch classes.
"""
devs_file = "devs.yml"

"""
Reset all the switches before starting the test.
If a switch was off by a previous test, the load_device_list process
will not find its associated DevSwitch object.

TODO: Due to the duality of hubs for USB 3.0 and USB 2.0 ports,
this may cause some power cycle to duplicate and report errors. 
In best case, this will just cause unnecessary power cycles.
"""
print("1. Resetting all switches before starting the test...")
DevSwitch.reset_all()

"""
Load the device list from the provided YAML file
"""
print(f"\n2. Loading device list from file: {devs_file}")
dev_list = Device.load_device_list_from_yml(devs_file)
for dev in dev_list:
    print(f"Device Name: {dev.name}, UID: {dev.uid}")
    if dev.access:
        print(f"  Address: {dev.access.get_address()}")
    if dev.switch:
        print(f"  Hub: {dev.switch.hub}, Port: {dev.switch.port}")
        print(f"  Status: {dev.switch.status()}")

""" 
Switch the first switchable device on the list
"""
print("\n3. Test switch off on first switchable device")
dev_0 = dev_list[0]

if dev_0.switch: 
    dev_0.switch.off()
    print(f"Status after switch off attempt: {dev_0.switch.status()}")
else:
    print("Device 0 has no associated switch.")

"""
Reset (power cycle) the second switchable device on the list
"""
print("\n4. Test reset action on second switchable device")
dev_1 = dev_list[1]

if dev_1.switch:
    dev_1.switch.reset()
    time.sleep(2)

    print(f"Status after reset attempt: {dev_1.switch.status()}")

"""
Scan all the available DevSwitch devices
"""
print("\n5. Scan all available DevSwitch devices...")
for dev in DevSwitch.scan():
    print(f"Scanned Device - Hub: {dev.hub}, Port: {dev.port}, Status: {dev.status()}")