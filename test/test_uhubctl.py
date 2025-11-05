"""
This is a basic manual test for the Uhubctl class.
Remember that the udev rules must be set properly to allow
non-root access to the USB hubs.
"""
import time
import sys
sys.path.append('..')

from uhubctl import Uhubctl

uhub = Uhubctl()

print("1. Scan hubs and ports")

hubs_ports_list = uhub.scan_hubs_ports()

print("Found the following hubs and ports:")

for (hub, port) in hubs_ports_list:
    status = uhub.get_status(hub, port)
    print(f"Status of Hub={hub}, Port={port}: {status}")

"""
Choose a device description substring to search for its hub and port
to test the search by description functionality.
In this example, we use the value "KitProg3" which is used by PSOCx
Infineon controllers devices.
"""
print("\n2. Search specific hub and port by device description")
desc_match = "KitProg3"
hub, port = uhub.get_hub_port_by_desc(desc_match)
print(f"Hub and port for device with desc match '{desc_match}': Hub={hub}, Port={port}")

""" 
Test some of the actions on the found hub and port.
"""
if hub and port:
    print("\n3. Test actions on the found hub and port")

    uhub.run_action(Uhubctl.Cmd.off, hub, port)
    print(f"Attempting to turn off Hub={hub}, Port={port}...", end=' ')
    assert(uhub.get_status(hub, port) == "off" )
    print("OK")
    time.sleep(2)

    uhub.run_action(Uhubctl.Cmd.on, hub, port)
    print(f"Attempting to turn on Hub={hub}, Port={port}...", end=' ')
    assert(uhub.get_status(hub, port) == "on" or uhub.get_status(hub, port) == "on connected")
    print("OK")
    time.sleep(2)  

    uhub.run_action(Uhubctl.Cmd.toggle, hub, port)
    print(f"Attempting to toggle Hub={hub}, Port={port}...", end=' ')
    assert(uhub.get_status(hub, port) == "off")
    print("OK")
    time.sleep(2)

    uhub.run_action(Uhubctl.Cmd.cycle, hub, port)
    print(f"Attempting to power cycle Hub={hub}, Port={port}...", end=' ')
    assert(uhub.get_status(hub, port) == "on" or uhub.get_status(hub, port) == "on connected")
    print("OK")