import dbus
import time

# Setup DBus system bus
bus = dbus.SystemBus()
adapter_path = '/org/bluez/hci0'
adapter = bus.get_object('org.bluez', adapter_path)
adapter_props = dbus.Interface(adapter, "org.freedesktop.DBus.Properties")

# Ensure adapter is powered on
if not adapter_props.Get('org.bluez.Adapter1', 'Powered'):
    adapter_props.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(True))
    print("Powered on Bluetooth adapter.")

# Start device discovery
adapter_iface = dbus.Interface(adapter, 'org.bluez.Adapter1')
manager = dbus.Interface(bus.get_object('org.bluez', '/'), 'org.freedesktop.DBus.ObjectManager')

print("Starting device discovery...")
adapter_iface.StartDiscovery()
time.sleep(7)
adapter_iface.StopDiscovery()
print("Discovery complete.\n")

# Define your target Bluetooth MAC address
target_address = ""  # Replace with your actual device address

# Locate target device
managed_objects = manager.GetManagedObjects()
device_list = {}

for obj_path, interfaces in managed_objects.items():
    if 'org.bluez.Device1' in interfaces:
        props = interfaces['org.bluez.Device1']
        address = props.get('Address')
        if address == target_address:
            device_list[address] = obj_path
            break

if target_address not in device_list:
    print("Target device not found.")
    exit()

# Connect to the device
device_path = device_list[target_address]
device = bus.get_object('org.bluez', device_path)
device_iface = dbus.Interface(device, 'org.bluez.Device1')

try:
    print(f"Connecting to {target_address}...")
    device_iface.Connect()
    print("✔ Connected.\n")
except dbus.DBusException as e:
    print(f"✘ Failed to connect: {e}")
    exit()

# Give the device a moment to register its GATT services
time.sleep(3)

# Define GATT characteristic path and payload (for "single color" control)
char_path = "/org/bluez/hci0/dev_D5_39_32_33_06_4B/service000e/char0013"  # Update if needed
hex_payload = "3301000000000000000000000000000000000032"  # Example: one color or command

# Send the payload
try:
    char_obj = bus.get_object('org.bluez', char_path)
    char_iface = dbus.Interface(char_obj, 'org.bluez.GattCharacteristic1')

    byte_data = dbus.Array([dbus.Byte(int(hex_payload[i:i+2], 16)) for i in range(0, len(hex_payload), 2)], signature='y')
    char_iface.WriteValue(byte_data, dbus.Dictionary({}, signature='sv'))

    print(f"✔ Payload sent: {hex_payload}")
except dbus.DBusException as e:
    print(f"✘ Failed to write payload: {e}")
