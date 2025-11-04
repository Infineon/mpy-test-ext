from dataclasses import dataclass
from serial.tools.list_ports import comports
from uhubctl import Uhubctl
import yaml
import os
import sys

def load_yml_file(file: str) -> dict:
    if not os.path.exists(file):
        print(f'error: YAML file "{file}" does not exist')
        sys.exit(1)

    try:
        with open(file, "r") as f:
            yml_dict = yaml.safe_load(f)
    except:
        print(f'error: unable to open YAML file "{file}"')
        sys.exit(1)

    return yml_dict

@dataclass
class DevSwitch:

    hub: str
    port: int
    hw_controller : object = Uhubctl()

    def on(self) -> None:
        self.hw_controller.run_action(Uhubctl.Cmd.on, self.hub, self.port)

    def off(self) -> None:
        self.hw_controller.run_action(Uhubctl.Cmd.off, self.hub, self.port)

    def reset(self) -> None:
        self.hw_controller.run_action(Uhubctl.Cmd.cycle, self.hub, self.port)

    def status(self) -> str:
        return self.hw_controller.get_status(self.hub, self.port)
    
    @classmethod
    def reset_all(cls) -> None:
        hubs_ports = cls.hw_controller.scan_hubs_ports()
        # TODO: Daisy chain and duplicated 3.0 ports will either
        # generate an error or cause unnecessary multiple resets.
        # But this is really a detail relative to uhubctl... This library should be
        # seen as a potential interface to device switches. 
        unique_hubs = set([hub for hub, port in hubs_ports])
        for hub in unique_hubs:
            cls.hw_controller.run_action(Uhubctl.Cmd.cycle, hub, None)

    @classmethod
    def create_from_uid(cls, uid: str) -> "DevSwitch":
        
        hub, port = cls.hw_controller.get_hub_port_by_desc(uid)
        
        if hub and port:
            return cls(hub=hub, port=port)
        
        return None
    
    @classmethod
    def scan(cls) -> list["DevSwitch"]:
        
        hub_port = cls.hw_controller.scan_hubs_ports()
        
        switch_list = []
        for (hub, port) in hub_port:
            switch_list.append(cls(hub=hub, port=port))
        
        return switch_list
    
@dataclass
class DevAccessSerial:

    address: str
    # TODO: Add additional requirements for accessibility:
    #     #       - the device is not busy (fuser or such as in makersHIL)

    def get_address(self) -> str:
        return self.address

    @classmethod
    def create_from_uid(cls, uid: str) -> "DevAccessSerial":
        for port in comports():
            if port.serial_number == uid:
                return cls(address=port.device)
        
        return None   
    
@dataclass
class Device:

    name: str
    uid: str
    features: list[str]
    access: DevAccessSerial = None
    switch: DevSwitch = None

    def __post_init__(self):
        self.access = DevAccessSerial.create_from_uid(self.uid)
        self.switch = DevSwitch.create_from_uid(self.uid)

    @classmethod
    def load_device_list_from_yml(cls, devs_yml_file: str) -> list["Device"]:
        dev_yml_dict = load_yml_file(devs_yml_file)
        
        dev_obj_list = []
        for dev in dev_yml_dict:
            device = Device(
                name=dev.get('name', ''),
                uid=dev.get('uid', ''),
                features=dev.get('features', []),
            )
            dev_obj_list.append(device)

        return dev_obj_list
