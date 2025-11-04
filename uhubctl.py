from enum import Enum
import re
import subprocess
from dataclasses import dataclass

class Uhubctl:
    """
    This class provides a wrapper around the uhubctl command-line tool
    to control USB hubs. It enables the power switching
    capabilities of a device. 
    The hub to with the device is connected must be supported in uhubctl.

    All the relevant information can be found in the uhubctl repository:
        https://github.com/mvp/uhubctl

    This class only implements the functionality needed by the
    SwitchDev class.
    """
    class Cmd(Enum):
        on = "on"
        off = "off"
        cycle = "cycle"
        toggle = "toggle"
    
    def __init__(self):
        self.last_cmd_output = ""

    def run_action(self, action: Cmd, hub: str, port: int) -> None:
        """
        Run the specified action on the given hub and port.
        Args:
            action: The action to perform (on, off, cycle, toggle)
            hub: The hub identifier (e.g., "1-1.3")
            port: The port number (e.g., 2)

        If port is None, the action is applied to all ports of the hub.
        If hub is None, the action is applied to all hubs. But port can not be None in this case.
        Returns:
            None
        """
        cmd = ["--action", action.value]
        if hub != None:
            cmd += ["--location", hub]
        if port != None:
            cmd += ["--port", f"{port}"]

        self.__run_cmd(cmd)

    def get_hub_port_by_desc(self, desc_match: str) -> tuple[str, int]:
        """
        Call uhubctl to get the hub location and port number for a given 
        string which is part of the device description in the device
        entry of the uhubctl output.

        Args:
            desc_match: Matching pattern or string appearing in the device description
        Returns:
            (hub, port) tuple if found, (None, None) if not found
        """
        self.__run_cmd(["--search", desc_match])
        
        return self.__output_search_hub_port_by_desc(desc_match)
    
    def get_status(self, hub: str, port: int) -> str:
        """
        Get the current status of this hub port.

        Args:
            hub: The hub identifier (e.g., "1-1.3")
            port: The port number (e.g., 2)
        Returns:
            "off" - Port is powered
            "on" - Port is powered on.
            "not connected" - Port is on but no device connected
            "unknown" - Could not determine status
        """
        self.__run_cmd(["--location", hub, "--port", f"{port}"])
        return self.__output_search_port_status(hub, port)
    
    def scan_hubs_ports(self) -> list[tuple[str, int]]:
        """ 
        Scan to find all available uhubctl compatible hubs and their ports.
        
        Returns:
            A list of (hub, port) tuples for all discovered ports.
        """
        self.__run_cmd([])
        return self.__output_scan_hub_ports()
    
    """
    Private methods
    """

    def __run_cmd(self, cmd_args: list[str]) -> None:
        """
        Run the uhubctl command with the specified arguments.

        If the stderror indicates that no devices are detected
        this is not considered an error. A USB hub may not be
        connected or available.

        Args:
            cmd_args: List of command-line arguments for uhubctl
        
        Returns:
            The standard output from the uhubctl command as a string.
            An empty string if no devices are detected or an error occurs.
        """
        uhub_cmd = ["uhubctl"] + cmd_args
        uhub_proc = subprocess.run(uhub_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        uhub_err = uhub_proc.stderr.decode('utf-8')

        if uhub_proc.returncode != 0:
            if not Uhubctl.__are_devices_detected(uhub_err):  
                self.last_cmd_output = ""
                return
            
            print(f"error: uhubctl command '{cmd_args}' failed")
            self.last_cmd_output = ""
    
        self.last_cmd_output =  uhub_proc.stdout.decode('utf-8')

    @staticmethod
    def __are_devices_detected(uhubctl_stderr : str) -> bool:
        """
        Parse uhubctl output to check if devices are found
        
        This method is used to avoid parsing further if no devices
        are detected by uhubctl.
        
        Example of expected uhubctl output when no devices are found:

            No compatible devices detected!
            Run with -h to get usage info.
        """
        if "No compatible devices detected!" in uhubctl_stderr:
            return False
        return True
    
    def __output_search_hub_port_by_desc(self, desc_match: str) -> tuple[str, int]:
        """
        Parse uhubctl output to find hub and port for given description match.
        
        Args:
            desc_match: Matching pattern or string appearing in the device description
        Returns:
            (hub, port) tuple if found, (None, None) if not found


        Example of expected uhubctl output format for a device with USB 3.0 duality
        (More info at https://github.com/mvp/uhubctl?tab=readme-ov-file#usb-30-duality-note)
        where a PSOC6 KitProg3 with serial number 1106035A012D2400 is connected:

            Current status for hub 2-1 [0bda:0411 Generic USB3.2 Hub, USB 3.20, 4 ports, ppps]
              Port 2: 02a0 power 5gbps Rx.Detect
            Current status for hub 1-1 [0bda:5411 Generic USB2.1 Hub, USB 2.10, 4 ports, ppps]
              Port 2: 0103 power enable connect [04b4:f155 Cypress Semiconductor KitProg3 CMSIS-DAP 1106035A012D2400]

        The method should return ("1-1", 2) for the above example when
        desc_match is "1106035A012D2400".
        """
        output_lines = self.last_cmd_output.strip().split('\n')
        current_hub = None
        
        for line in output_lines:
            line = line.strip()
            
            current_hub = Uhubctl.__line_search_update_hub(line, current_hub)
            current_port = Uhubctl.__line_search_port(line)

            if current_hub and current_port and desc_match in line :
                return (current_hub, current_port)
        
        return (None, None)

    def __output_search_port_status(self, hub: str, port: int) -> str:
        """
        Get the current status of this hub port.

        Args:
            hub: The hub identifier (e.g., "1-1.3")
            port: The port number (e.g., 2)
        Returns:
            "off" - Port is powered off
            "on" - Port is powered on.
            "not connected" - Port is on but no device connected 
            "unknown" - Could not determine status 

        Example of expected uhubctl output for a set of ports with different statuses.
        For hub 2-1, only port 3 and 4 have devices connected.
        For hub 1-1.3, only port 3 has a device connected, and the port 1 is off.
        The rest of the ports are powered on but no device is connected.
        
            Current status for hub 2-1 [0bda:0411 Generic USB3.2 Hub, USB 3.20, 4 ports, ppps]
              Port 1: 02a0 power 5gbps Rx.Detect
              Port 2: 02a0 power 5gbps Rx.Detect
              Port 3: 0263 power 5gbps U3 enable connect [0bda:0411 Generic USB3.2 Hub, USB 3.20, 4 ports, ppps]
              Port 4: 0263 power 5gbps U3 enable connect [0bda:0411 Generic USB3.2 Hub, USB 3.20, 4 ports, ppps]
            Current status for hub 1-1.3 [0bda:5411 Generic USB2.1 Hub, USB 2.10, 4 ports, ppps]
              Port 1: 0100 off
              Port 2: 0100 power
              Port 3: 0103 power enable connect [04b4:f155 Cypress Semiconductor KitProg3 CMSIS-DAP 0D170C5A012D2400]
              Port 4: 0100 power

        As seen above, the status is the after the port number and the code number. Sometimes it also 
        includes additional information like the speed of certain usb status.

        """
        output_lines = self.last_cmd_output.strip().split('\n')
        current_hub = None

        for line in output_lines:
            line = line.strip()
           
            current_hub = Uhubctl.__line_search_update_hub(line, current_hub)
            current_port = Uhubctl.__line_search_port(line)

            if hub == current_hub and port == current_port:                
                if " off" in line:
                    return "off"
                elif " power" in line and  "enable connect" in line:
                    return "on connected"
                elif " power" in line:
                    return "on"
                else:
                    return "unknown"
        
        return "unknown"
    
    def __output_scan_hub_ports(self) -> list[tuple[str, int]]:
        """ 
        Scan to find all available uhubctl compatible hubs and their ports.
        Returns:
            A list of (hub, port) tuples for all discovered ports.
        """
        discovered_ports = []
        output_lines = self.last_cmd_output.strip().split('\n')
        current_hub = None

        for line in output_lines:
            line = line.strip()
            
            current_hub = Uhubctl.__line_search_update_hub(line, current_hub)
            current_port = Uhubctl.__line_search_port(line)

            if current_hub and current_port:
                discovered_ports.append((current_hub, current_port))
        
        return discovered_ports

    @staticmethod
    def __line_search_update_hub(output_line : str, current_hub: str) -> str:
        """
        Search in a line for the hub value and update it to be the
        current hub if found.

        The hub line is the start of the section for a given hub and all 
        it ports. The function will be run over all output lines, but only
        update the hub value when a hub line is found.
        That is the start of a new hub section, and the next lines will 
        contain the ports for that hub.

        Args:
            output_line: The current output line to parse
            current_hub: The current hub value, to be updated if a hub line is found.

        Returns:
            The updated hub value if found, otherwise the current_hub value.
        """
        if output_line.startswith("Current status for hub"):
            hub_match = re.search(r'hub (\S+)', output_line)
            if hub_match:
                return hub_match.group(1)
        return current_hub

    @staticmethod        
    def __line_search_port(output_line : str) -> int:
        """
        Search in a line for the port number.

        Args:
            output_line: The current output line to parse
        Returns:
            The port number if found, otherwise None.
        """
        port_number = None
        if output_line.startswith("Port"):
            port_match = re.search(r'Port (\d+):', output_line)
            if port_match:
                    port_number = int(port_match.group(1))

        return port_number