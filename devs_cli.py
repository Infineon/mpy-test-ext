import argparse
from devs import Device, DevSwitch, DevAccessSerial

# def filter_devices(devices, filter_expr):
#     """
#     Parse filter expression like 'name=esp32' and return matching devices
#     """
#     if '=' not in filter_expr:
#         raise ValueError("Filter must be in format 'attribute=value'")
    
#     attr_name, attr_value = filter_expr.split('=', 1)
#     return [dev for dev in devices if getattr(dev, attr_name, None) == attr_value]

# def get_device_attributes(devices, attribute):
#     """Extract specific attribute from device list"""
#     return [getattr(dev, attribute) for dev in devices if hasattr(dev, attribute)]

# def parser_get_device_uids(args):
#     """Get device UIDs based on filter"""
#     devices = Device.load_device_list_from_yml(args.devs_yml)
    
#     if args.filter:
#         devices = filter_devices(devices, args.filter)
    
#     uids = get_device_attributes(devices, 'uid')
#     print(*uids)

# def parser():
#     parser = argparse.ArgumentParser(description="Device query utility")
#     subparser = parser.add_subparsers()

#     # Add UID command
#     parser_uid = subparser.add_parser("uid", description="Get device UIDs")
#     parser_uid.add_argument("-y", "--devs-yml", required=True, help="Device YAML file")
#     parser_uid.add_argument("--filter", help="Filter in format 'attribute=value'")
#     parser_uid.set_defaults(func=parser_get_device_uids)

#     args = parser.parse_args()
#     args.func(args)

# if __name__ == "__main__":
#     parser()

# dev_list = Device.s("devs.yml")

# devs_cli.py uid -filter name=xxxx --devs-yml devs.yml

# def parser():
#     def main_parser_func(args):
#         parser.print_help()

#     def parse_validate_opt_arg_mutual_required(args):
#         if args.devs_yml and args.board is None:
#             parser.error("--devs-yml requires --board.")
#         if args.board and args.devs_yml is None:
#             parser.error("--board requires --dev-yml.")
#         if args.hw_ext is not None and (args.board is None or args.devs_yml is None):
#             parser.error("--hw_ext requires --board and --dev-yml.")

#     def parser_get_devices_serial_num(args):
#         parse_validate_opt_arg_mutual_required(args)
#         devs_serial = get_devices_serial_num(args.board, args.devs_yml, args.hw_ext)
#         print(*devs_serial)

#     def parser_get_devices_port(args):
#         parse_validate_opt_arg_mutual_required(args)
#         devs_port = get_devices_port(args.board, args.devs_yml, args.hw_ext)
#         print(*devs_port)

#     parser = argparse.ArgumentParser(description="Get kitprog3 device utility")

#     subparser = parser.add_subparsers()
#     parser.set_defaults(func=main_parser_func)

#     # Get devices serial numbers
#     parser_sn = subparser.add_parser(
#         "serial-number", description="Get kitprog3 devices serial number list"
#     )
#     parser_sn.add_argument("-b", "--board", type=str, help="Board name")
#     parser_sn.add_argument(
#         "-y", "--devs-yml", type=str, help="Device list yml with board - serial number map"
#     )
#     parser_sn.add_argument(
#         "--hw-ext", type=str, default=None, help="Required external hardware configuration"
#     )
#     parser_sn.set_defaults(func=parser_get_devices_serial_num)

#     # Get devices port
#     parser_port = subparser.add_parser("port", description="Get kitprog3 devices port list")
#     parser_port.add_argument("-b", "--board", type=str, help="Board name")
#     parser_port.add_argument(
#         "-y", "--devs-yml", type=str, help="Device list yml with board - serial number map"
#     )
#     parser_port.add_argument(
#         "--hw-ext", type=str, default=None, help="Required external hardware configuration"
#     )
#     parser_port.set_defaults(func=parser_get_devices_port)

#     # Parser call
#     args = parser.parse_args()
#     args.func(args)

# if __name__ == "__main__":

#     from serial.tools.list_ports import comports

#     # List all available attributes
#     for port in comports():
#         print(f"Device: {port.device}")
#         print(f"Name: {port.name}")
#         print(f"Description: {port.description}")
#         print(f"Serial Number: {port.serial_number}")
#         print(f"Manufacturer: {port.manufacturer}")
#         print(f"Product: {port.product}")
#         print(f"VID: {port.vid}")
#         print(f"PID: {port.pid}")
#         print(f"Location: {port.location}")
#         print(f"HWID: {port.hwid}")
#         print("-" * 40)

class DevsQuery:

    def __init__(self, devs_yml: str):
        self.dev_list = Device.load_device_list_from_yml(devs_yml)

    def query(self, query_attr, attr_name: str, attr_value: str) -> list[str]:
        """
        Query devices by attribute name and value, returning their UIDs.
        """
        # if there is a filter
            # check if the filter attribute is matching
            # if not it can be an attribute of the access object
            # call the access object querier

        # if it has attribute return. 

        # Otherwise it can be an attribute of the access object
        
        return [
            dev.uid for dev in self.dev_list
            if getattr(dev, attr_name, None) == attr_value
        ]
    
class DevsSerialQuery: 


    def query(self, query_attr, attr_name: str, attr_value: str) -> list[str]:
        """
        Query devices by attribute name and value, returning their serial access addresses.
        """
        return [
            dev.access.get_address() for dev in self.dev_list
            if getattr(dev, attr_name, None) == attr_value and dev.access is not None
        ]

class DevsQueryCLI:

    def __init__(self):

        parser = argparse.ArgumentParser(description="Device query utility")
        subparser = parser.add_subparsers()

        # Add UID command
        parser = subparser.add_parser("query_attr", description="Get device UIDs")
        parser.add_argument("-f", "--filter", help="Filter in format 'attribute=value'") 
        parser.add_argument("-y", "--devs-yml", required=True, help="Device YAML file")

    def parse(self) -> argparse.Namespace:
        """
        Parse the command line arguments and validate them.
        It also sets the default values for the arguments if not provided.
        """
        args = self.parser.parse_args()
        args = self.__set_validate_args(args)
        return args

# if --devs-yml load the device list from the provided YAML file
# it will show all the connected devices

# if --filter is provided, it will filter the devices based on the attribute=value
 # the filter can be a device attribute
 # or can be DevSerialAccess attribute