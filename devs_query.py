import argparse
from dataclasses import dataclass 
from devs import Device, DevAccessSerial, DevSwitch

class ObjectAttrQuerier: 
    """
    A utility class to query attributes from an object, including nested objects.
    It supports exact and partial matching, as well as filtering based on multiple criteria.
    """

    @dataclass
    class AttrQueryFilter:
        """
        A data class to represent a filter for attribute querying.
        """
        attr_key: str
        attr_value: str = None
        exact: bool = True

    def __init__(self, obj):
        """
        Initialize the ObjectAttrQuerier with the target object.
        """
        self.obj = obj
    
    def query(self, attr_key: str, attr_value: str = None, exact: bool = True) -> object:
        """
        Query the attribute of the object.  
        If attr_value is provided, it checks for exact or partial match based on the 'exact' flag."""
        if attr_value:
            if exact:
                return (attr_value if self.__query_exact(attr_key, attr_value) else None)
            else:
                return (attr_value if self.__query_contains(attr_key, attr_value) else None)
        else:
            return self.__query_attr(attr_key)
        
    def query_deep(self, attr_key: str, attr_value: str = None, exact: bool = True) -> object:
        """
        Deep query the attribute of the object, including nested objects.
        If attr_value is provided, it checks for exact or partial match based on the 'exact' flag.
        """
        found_attr_value = self.query(attr_key, attr_value, exact)

        if not found_attr_value:
            for attr in vars(self.obj):
                attr_obj = getattr(self.obj, attr)
                if isinstance(attr_obj, object):
                    sub_querier = ObjectAttrQuerier(attr_obj)
                    found_attr_value = sub_querier.query(attr_key, attr_value, exact)
                    if found_attr_value is not None:
                        return found_attr_value
        
        return found_attr_value

    def query_filtered(self, attr_key, query_filter_list: list[AttrQueryFilter], deep: bool = False) -> object:
        """
        Query the attribute of the object with multiple filters.
        If deep is True, it performs a deep query.
        """
        query_func = self.query_deep if deep else self.query

        attr_value = query_func(attr_key)
        if not attr_value:
            return None
        
        for query_filter in query_filter_list:
            filter_attr_value = query_func(query_filter.attr_key, query_filter.attr_value, query_filter.exact)
            if not filter_attr_value:
                return None
            
        return attr_value
    
    @staticmethod
    def query_list(obj_list: list[object], attr_key, query_filter_list: list[AttrQueryFilter] = [], deep: bool = False) -> list[object]:
        """
        Query a list of objects for a specific attribute with optional filters.
        If deep is True, it performs a deep query."""
        query_list = []
        for obj in obj_list:
            obj = ObjectAttrQuerier(obj)
            attr_value = obj.query_filtered(attr_key, query_filter_list, deep)
            if attr_value:
                query_list.append(attr_value)

        return query_list

    """ 
    Private methods     
    """
    def __query_attr(self, query_attr: str) -> object:
        """
        Query the attribute of the object.
        """
        if hasattr(self.obj, query_attr):
            return getattr(self.obj, query_attr)
        
        return None
    
    def __query_exact(self, query_attr: str, query_value: str) -> bool:
        """
        Check if the attribute of the object matches exactly the query value.
        """
        if hasattr(self.obj, query_attr):
            return getattr(self.obj, query_attr) == query_value
        
        return False
    
    def __query_contains(self, query_attr: str, query_value: str) -> bool:
        """
        Check if the attribute of the object contains the query value.
        """
        if hasattr(self.obj, query_attr):
            attr_value = getattr(self.obj, query_attr)
            if isinstance(attr_value, str):
                return query_value in attr_value
        
        return False

class DevsQueryCLI:
    """
    A command-line interface (CLI) for querying device attributes using ObjectAttrQuerier.
    The allowed device objects are Device, DevAccessSerial, and DevSwitch.
    """
    def __init__(self):

        self.allowed_dev_objs = [Device, DevAccessSerial, DevSwitch] 
        self.parser = argparse.ArgumentParser(description="Device query utility")

        self.parser.add_argument("query_attribute", choices=self.__get_query_choices(), help="The attribute to query from the devices.")
        self.parser.add_argument("-f", "--filter", nargs="*", action="append", help="Filter in format 'attribute_key=attribute_value'. It accepts multiple filters separated by space, or multiple -f options.") 
        self.parser.add_argument("-y", "--devs-yml", default=None, help="Device YAML file. If not provided, it query from the connected serial devices.")
        self.parser.add_argument("--not-connected", default=False, action="store_true", help="Include also NOT connected devices from the device list. Only relevant when using --devs-yml")

    def parse(self) -> argparse.Namespace:
        """
        Parse and validate the command-line arguments.
        """
        args = self.parser.parse_args()
        self.__set_validate_args(args)
        return args
    
    def __get_query_choices(self) -> list[str]:
        """
        Get the list of possible attribute names from the allowed device objects.
        The valid attributes are those with string or integer types.
        """
        def get_obj_attributes(obj):
            attr_list = []
            for attr in dir(obj):
                if not callable(getattr(obj, attr)) and not attr.startswith("__"):
                    if isinstance(getattr(obj, attr), str) or isinstance(getattr(obj, attr), int):
                        attr_list.append(attr)
                    
            if hasattr(obj, '__annotations__'):
                for attr, attr_type in obj.__annotations__.items():
                    # Check if it's a string type
                    if attr_type == str or attr_type == 'str' or attr_type == int or attr_type == 'int':
                        attr_list.append(attr)
                
                return attr_list

        choices = []
        for obj in self.allowed_dev_objs:
            choices.extend(get_obj_attributes(obj))
         
        choices = sorted(list(set(choices)))

        return choices
    
    def __set_validate_args(self, args: argparse.Namespace) -> argparse.Namespace:
        """
        Validate and set the command-line arguments.
        The filters must be in the format 'attribute=value'.
        As the CLI allows multiple -f options and the append action, it flatten
        the list of lists into a single list.
        """
        if args.filter:
            simple_filter_list = []
            for filter in args.filter:
                if not isinstance(filter, list):
                    simple_filter_list.append(filter)
                else:
                    simple_filter_list.extend(filter)

            args.filter = simple_filter_list
            for f in simple_filter_list:
                if '=' not in f:
                    self.parser.error("filter must be in format 'attribute=value'")

    def parse_filters(self, filter_str_list: list[str]) -> list[ObjectAttrQuerier.AttrQueryFilter]:
        """
        Parse the filter strings into a list of AttrQueryFilter objects.
        Each filter string must be in the format 'attribute=value'.
        """
        filter_list = []
        for filter_str in filter_str_list:

            attr_name, attr_value = filter_str.split('=', 1)
            filter_list.append(ObjectAttrQuerier.AttrQueryFilter(attr_key=attr_name, attr_value=attr_value))
        
        return filter_list
            

def main_devs_query_cli() -> list[str]:
    """
    Main function for the DevsQueryCLI.
    It parses the command-line arguments, loads the device list,
    applies the queries and filters, and prints the results.

    If a device YAML file is provided, it loads the device list from the file.
    Otherwise, it scans for connected serial devices.
    """
    cli = DevsQueryCLI()
    args = cli.parse()

    query_filter_list = []
    if args.filter:
        query_filter_list = cli.parse_filters(args.filter)

    if args.devs_yml:
        dev_list = Device.load_device_list_from_yml(args.devs_yml)
        if not args.not_connected:
            dev_list =[ dev for dev in dev_list if dev.access is not None ]
    else:
        dev_list = DevAccessSerial.scan()

    query_list = ObjectAttrQuerier.query_list(
        dev_list,
        args.query_attribute,
        query_filter_list,
        deep=True
    )

    print(*query_list)
    
if __name__ == "__main__":
    main_devs_query_cli()