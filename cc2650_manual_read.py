# -*- coding: utf-8 -*-
"""
TI CC2650 SensorTag
-------------------

Adapted by Ashwin from the following sources:
 - https://github.com/IanHarvey/bluepy/blob/a7f5db1a31dba50f77454e036b5ee05c3b7e2d6e/bluepy/sensortag.py
 - https://github.com/hbldh/bleak/blob/develop/examples/sensortag.py

"""
import asyncio
import datetime
import platform
import struct

light_value = 0

from bleak import BleakClient


class Service:
    """
    Here is a good documentation about the concepts in ble;
    https://learn.adafruit.com/introduction-to-bluetooth-low-energy/gatt

    In TI SensorTag there is a control characteristic and a data characteristic which define a service or sensor
    like the Light Sensor, Humidity Sensor etc

    Please take a look at the official TI user guide as well at
    https://processors.wiki.ti.com/index.php/CC2650_SensorTag_User's_Guide
    """

    def __init__(self):
        self.data_uuid = None
        self.ctrl_uuid = None
        self.period_uuid = None


class Sensor(Service):

    def callback(self, sender: int, data: bytearray):
        raise NotImplementedError()

    async def enable(self, client, *args):
        # start the sensor on the device
        write_value = bytearray([0x01])
        await client.write_gatt_char(self.ctrl_uuid, write_value)
        write_value = bytearray([0x0A])
        await client.write_gatt_char(self.period_uuid, write_value)

        return self

    async def read(self, client):
        val = await client.read_gatt_char(self.data_uuid)
        return self.callback(1, val)


class OpticalSensor(Sensor):
    def __init__(self):
        super().__init__()
        self.data_uuid = "f000aa71-0451-4000-b000-000000000000"
        self.ctrl_uuid = "f000aa72-0451-4000-b000-000000000000"
        self.period_uuid = "f000aa73-0451-4000-b000-000000000000"

    def callback(self, sender: int, data: bytearray):
        tt = datetime.datetime.now()
        raw = struct.unpack('<h', data)[0]
        m = raw & 0xFFF
        e = (raw & 0xF000) >> 12
        # print(f"[OpticalSensor @ {tt}] Reading from light sensor: {0.01 * (m << e)}")
        return 0.01 * (m << e)

class BarometerSensor(Sensor):
    def __init__(self):
        super().__init__()
        self.data_uuid = "f000aa41-0451-4000-b000-000000000000"
        self.ctrl_uuid = "f000aa42-0451-4000-b000-000000000000"
        self.period_uuid = "f000aa43-0451-4000-b000-000000000000"

    def callback(self, sender: int, data: bytearray):
        (tL, tM, tH, pL, pM, pH) = struct.unpack('<BBBBBB', data)
        temp = (tH*65536 + tM*256 + tL) / 100.0
        press = (pH*65536 + pM*256 + pL) / 100.0
        #print(f"[BarometerSensor] Ambient temp: {temp}; Pressure Millibars: {press}")
        return temp, press

class HumiditySensor(Sensor):
    def __init__(self):
        super().__init__()
        self.data_uuid = "f000aa21-0451-4000-b000-000000000000"
        self.ctrl_uuid = "f000aa22-0451-4000-b000-000000000000"
        self.period_uuid = "f000aa23-0451-4000-b000-000000000000"

    def callback(self, sender: int, data: bytearray):
        (rawT, rawH) = struct.unpack('<HH', data)
        temp = -40.0 + 165.0 * (rawT / 65536.0)
        RH = 100.0 * (rawH/65536.0)
        # print(f"[HumiditySensor] Ambient temp: {temp}; Relative Humidity: {RH}")
        return temp, RH

class GyrometerSensor(Sensor):
    def __init__(self):
        super().__init__()
        self.data_uuid = "f000aa51-0451-4000-b000-000000000000"
        self.ctrl_uuid = "f000aa52-0451-4000-b000-000000000000"
        self.period_uuid = "f000aa33-0451-4000-b000-000000000000"
        self.scale = 500.0/65536.0

    def callback(self, sender: int, data: bytearray):
        (x,y,z) = struct.unpack('<BBB', data)

        #print(f"[BarometerSensor] Ambient temp: {temp}; Pressure Millibars: {press}")
        return z*self.scale


async def run(address):
    async with BleakClient(address) as client:
        x = await client.is_connected()
        print("Connected: {0}".format(x))

        global light_value

        light_sensor = await OpticalSensor().enable(client)
        #humidity_sensor = await HumiditySensor().enable(client)
        barometer_sensor = await BarometerSensor().enable(client)
        #gyro_sensor = await GyrometerSensor().enable(client)

        while True:
            # await asyncio.sleep(0.08)
            data = await asyncio.gather(light_sensor.read(client), barometer_sensor.read(client))
            light_value = data[0]
            print(data)

def temperature_check():
    global light_value
    return "36"

if __name__ == "__main__":
    """
    To find the address, once your sensor tag is blinking the green led after pressing the button, run the discover.py
    file which was provided as an example from bleak to identify the sensor tag device
    """

    import os

    os.environ["PYTHONASYNCIODEBUG"] = str(1)
    address = (
        "54:6c:0e:b5:56:00"
        if platform.system() != "Darwin"
        else "6FFBA6AE-0802-4D92-B1CD-041BE4B4FEB9"
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(address))
    loop.run_forever()
