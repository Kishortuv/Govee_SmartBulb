import dbus
import time

# Connect to the system bus (DBus)
bus = dbus.SystemBus()

# Get the adapter object
adapter_path = '/org/bluez/hci0'
adapter = bus.get_object('org.bluez', adapter_path)
interface_properties = dbus.Interface(adapter, "org.freedesktop.DBus.Properties")

# Ensure the adapter is powered on
if not interface_properties.Get('org.bluez.Adapter1', 'Powered'):
    print("Powering on the adapter...")
    interface_properties.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(True))
else:
    print("Bluetooth adapter is already powered on.")

# Discovering available devices
discover = dbus.Interface(adapter, 'org.bluez.Adapter1')
discover.StartDiscovery()
print("Start discovery")
time.sleep(7)  # Wait for 5 seconds to discover devices
discover.StopDiscovery()
print("Discovery stopped")

# Get all managed objects from BlueZ
manager = dbus.Interface(bus.get_object('org.bluez', '/'), 'org.freedesktop.DBus.ObjectManager')
managed_objects = manager.GetManagedObjects()

# Initialize device list
device_list = {}

# Loop through managed objects to find devices
for device_path, ifaces in managed_objects.items():
    if 'org.bluez.Device1' in ifaces:  # Check if the object has the Device1 interface
        device = bus.get_object('org.bluez', device_path)
        device_properties = dbus.Interface(device, 'org.freedesktop.DBus.Properties')

        try:
            # Fetch properties of the device
            properties = device_properties.GetAll('org.bluez.Device1')

            # Get the Bluetooth address (MAC address)
            bt_address = properties.get('Address')

            # Get the device name
            name = properties.get('Name')

            # Get the RSSI (Received Signal Strength Indicator)
            rssi = properties.get('RSSI') if 'RSSI' in properties else "N/A"  # RSSI might not always be available

            # Add the device to the device_list dictionary for easy lookup
            device_list[bt_address] = {'Name': name, 'RSSI': rssi, 'Path': device_path}

            # Print the device details
            print(f"Device Name: {name}")
            print(f"Bluetooth Address: {bt_address}")
            print(f"RSSI: {rssi}")
            print("-" * 50)

        except dbus.DBusException as e:
            print(f"Failed to get properties for {device_path}: {e}")

# Automatically connect to a specific device if it's found
bd_address = ""  # Example address (use your target device address)

if bd_address in device_list:
    print(f"Connecting to {device_list[bd_address]['Name']} at {bd_address}...")
    
    # Get the device object for the selected device
    device_path = device_list[bd_address]['Path']
    device = bus.get_object('org.bluez', device_path)

    # Get the Device1 interface and call the Connect method
    device_interface = dbus.Interface(device, 'org.bluez.Device1')
    try:
        # Attempt to connect to the device
        device_interface.Connect()
        print(f"Successfully connected to {device_list[bd_address]['Name']} at {bd_address}")
    except dbus.DBusException as e:
        print(f"Failed to connect to the device: {e}")

# Give the device time to expose its GATT services
time.sleep(3)

# Specify the GATT characteristic path directly
char_path = "/org/bluez/hci0/dev_D5_39_32_33_06_4B/service000e/char0013"

# Get the characteristic object
char_obj = bus.get_object('org.bluez', char_path)
char_props = dbus.Interface(char_obj, 'org.freedesktop.DBus.Properties')
char_iface = dbus.Interface(char_obj, 'org.bluez.GattCharacteristic1')

# Fetch the properties of the characteristic
props = char_props.GetAll('org.bluez.GattCharacteristic1')

# Print out the flags to check if it's writable
flags = props.get('Flags', [])
print(f"Characteristic Flags: {flags}")

# Check if the characteristic is writable
if "write" in flags or "write-without-response" in flags:
    print("Writable characteristic found. Sending write requests...")

    # Define the hex payloads to send
    """hex_payloads = [ 
                    "33050d00ff0000000000000000000000000000c4",
                    "33050500800000000000000000000000000000b3",
                    "33050500fe0000000000000000000000000000cd",
                    "3305050041000000000000000000000000000072",
                    "33050500bf00000000000000000000000000008c",
                    "33050d00ff0000000000000000000000000000c4"
                    ]"""


    hex_payloads = [
        "33050d00ff0000000000000000000000000000c4",
        "33050d00ffff000000000000000000000000003b",
        "33050d8b00ff000000000000000000000000004f",
        "3305046400000000000000000000000000000056",
        "3305050100000000000000000000000000000032",
        "33050500fe0000000000000000000000000000cd",
        "3305050041000000000000000000000000000072",
        "33050500bf00000000000000000000000000008c",
        "330505000000aa00000000000000000000000099",
        "330505000a00140000000000000000000000002d",
        "330505008a00fe00000000000000000000000047",
        "330505002e00560000000000000000000000004b",
        "330505004f4f4f0000000000000000000000007c",
        "330505006a6a6a00000000000000000000000059",
        "33050500800000000000000000000000000000b3",
        "33050d00ffff000000000000000000000000003b",
        "330505000000aa00000000000000000000000099",
        "33050d8b00ff000000000000000000000000004f",
        "330505002e00560000000000000000000000004b",
        "3305046400000000000000000000000000000056",
        "33050500800000000000000000000000000000b3",
        "330505000000aa00000000000000000000000099",
        "330505006a6a6a00000000000000000000000059",
        "3305050100000000000000000000000000000032",
        ]
    i = 0
    for i in range(0,4):
        # Loop through the hex payloads and write to the characteristic

        for hex_str in hex_payloads:
            try:
                # Convert hex string to byte array
                byte_data = dbus.Array([dbus.Byte(int(hex_str[i:i+2], 16)) for i in range(0, len(hex_str), 2)], signature='y')
                options = dbus.Dictionary({}, signature='sv')

                print(f"→ Writing: {hex_str}")
                # Write the byte data to the characteristic
                print("coming",i)
                char_iface.WriteValue(byte_data, options)
                print("✔ Write successful.")
                time.sleep(0.1)  # Optional delay between writes

            except dbus.DBusException as e:
                print(f"✘ Failed to write {hex_str}: {e}")
else:
    print("Characteristic is not writable — skipping.")

print("\nAll write requests sent.")

