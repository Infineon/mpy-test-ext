"""
This is a basic during development test for the ObjectAttrQuerier class.
It is not meant as a formal and thorough unit and coverage testing.
It just exercises the main functionalities of the class in 
a sunny-day testing approach.

In it we create a couple of Device and DevAccessSerial objects
and use them to test the querying functionalities of the ObjectAttrQuerier class.
"""
import sys

sys.path.append('..')

from devs_query import ObjectAttrQuerier
from devs import DevAccessSerial, Device

serial_dev_list = [
    DevAccessSerial(address="/dev/ttyACM1", serial_number="1106035A012D2400"),
    DevAccessSerial(address="/dev/ttyACM0", serial_number="0D170C5A012D2400")
]

dev_list = [
    Device(name="CY8CKIT-062S2-AI", uid="1106035A012D2400", features=["psoc6", "ble"], access=serial_dev_list[0]),
    Device(name="CY8CKIT-062S2-AI", uid="0D170C5A012D2400", features=["0.1.0.c"], access=serial_dev_list[1])
]
dev_querier = ObjectAttrQuerier(dev_list[0])

print("---- query ---")  
assert(dev_querier.query("name") == "CY8CKIT-062S2-AI")
assert(dev_querier.query("uid") == "1106035A012D2400")
assert(dev_querier.query("features") == ["psoc6", "ble"])
assert(dev_querier.query("access") == serial_dev_list[0])
assert(dev_querier.query("switch") == None)
assert(dev_querier.query("serial_number") ==  None)
assert(dev_querier.query("address") == None)

print("---- deep query ---")    
assert(dev_querier.query_deep("name") == "CY8CKIT-062S2-AI")
assert(dev_querier.query_deep("uid") == "1106035A012D2400")
assert(dev_querier.query_deep("features") == ["psoc6", "ble"])
assert(dev_querier.query_deep("access") == serial_dev_list[0])
assert(dev_querier.query_deep("switch") == None)
assert(dev_querier.query_deep("serial_number") == "1106035A012D2400")
assert(dev_querier.query_deep("address") == "/dev/ttyACM1")

print("---- filtered query ---")
filter_list = [
    ObjectAttrQuerier.AttrQueryFilter(attr_key="serial_number", attr_value="1106035A012D2400", exact=True),
    ObjectAttrQuerier.AttrQueryFilter(attr_key="address", attr_value="/dev/ttyACM1", exact=True),
    ObjectAttrQuerier.AttrQueryFilter(attr_key="name", attr_value="CY8CKIT-062S2-AI", exact=True)
]
assert(dev_querier.query_filtered("address", filter_list, deep=True) == "/dev/ttyACM1")
assert(dev_querier.query_filtered("address", filter_list) == None)
assert(dev_querier.query_filtered("serial_number", filter_list, deep=True) == "1106035A012D2400")
assert(dev_querier.query_filtered("serial_number", filter_list) == None)
assert(dev_querier.query_filtered("name", filter_list, deep=True) == "CY8CKIT-062S2-AI")

filter_list = [
    ObjectAttrQuerier.AttrQueryFilter(attr_key="address", attr_value="/dev/tty", exact=False)
]

assert(dev_querier.query_filtered("address", filter_list, deep=True) == "/dev/ttyACM1")

print("---- filtered query list ---")

filter_list = [
    ObjectAttrQuerier.AttrQueryFilter(attr_key="serial_number", attr_value="0D170C5A012D2400")
]

found_query_list = ObjectAttrQuerier.query_list(dev_list, "address", filter_list, deep=True)
assert(len(found_query_list) == 1)
assert("/dev/ttyACM0" in found_query_list)

found_query_list = ObjectAttrQuerier.query_list(dev_list, "address")
assert(len(found_query_list) == 0)

found_query_list = ObjectAttrQuerier.query_list(dev_list, "address", [], deep=True)
assert(len(found_query_list) == 2)




