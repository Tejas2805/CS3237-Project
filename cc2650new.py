# -*- coding: utf-8 -*-
"""
TI CC2650 SensorTag
-------------------

Adapted by Ashwin from the following sources:
 - https://github.com/IanHarvey/bluepy/blob/a7f5db1a31dba50f77454e036b5ee05c3b7e2d6e/bluepy/sensortag.py
 - https://github.com/hbldh/bleak/blob/develop/examples/sensortag.py

"""
import asyncio
import platform
import struct
import time

import picture_click as camera

from bleak import BleakClient

global indicator
global temp_store

light_just_opened = False
light_value = 0
gyro_z_just_opened = False
gyro_z_value = 0
gyro_z_first_confo = False
mag_value = 0
mag_just_opened= False
scam = False

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


class Sensor(Service):

    def callback(self, sender: int, data: bytearray):
        raise NotImplementedError()

    async def start_listener(self, client, *args):
        # start the sensor on the device
        write_value = bytearray([0x01])
        await client.write_gatt_char(self.ctrl_uuid, write_value)

        # listen using the handler
        await client.start_notify(self.data_uuid, self.callback)


class MovementSensorMPU9250SubService:

    def __init__(self):
        self.bits = 0

    def enable_bits(self):
        return self.bits

    def cb_sensor(self, data):
        raise NotImplementedError


class MovementSensorMPU9250(Sensor):
    GYRO_XYZ = 7
    ACCEL_XYZ = 7 << 3
    MAG_XYZ = 1 << 6
    ACCEL_RANGE_2G  = 0 << 8
    ACCEL_RANGE_4G  = 1 << 8
    ACCEL_RANGE_8G  = 2 << 8
    ACCEL_RANGE_16G = 3 << 8

    def __init__(self):
        super().__init__()
        self.data_uuid = "f000aa81-0451-4000-b000-000000000000"
        self.ctrl_uuid = "f000aa82-0451-4000-b000-000000000000"
        self.ctrlBits = 0

        self.sub_callbacks = []

    def register(self, cls_obj: MovementSensorMPU9250SubService):
        self.ctrlBits |= cls_obj.enable_bits()
        self.sub_callbacks.append(cls_obj.cb_sensor)

    async def start_listener(self, client, *args):
        # start the sensor on the device
        await client.write_gatt_char(self.ctrl_uuid, struct.pack("<H", self.ctrlBits))

        # listen using the handler
        await client.start_notify(self.data_uuid, self.callback)

    def callback(self, sender: int, data: bytearray):
        unpacked_data = struct.unpack("<hhhhhhhhh", data)
        for cb in self.sub_callbacks:
            cb(unpacked_data)


class AccelerometerSensorMovementSensorMPU9250(MovementSensorMPU9250SubService):
    def __init__(self):
        super().__init__()
        self.bits = MovementSensorMPU9250.ACCEL_XYZ | MovementSensorMPU9250.ACCEL_RANGE_4G
        self.scale = 8.0/32768.0 # TODO: why not 4.0, as documented? @Ashwin Need to verify

    def cb_sensor(self, data):
        '''Returns (x_accel, y_accel, z_accel) in units of g'''
        rawVals = data[3:6]
       # print("[MovementSensor] Accelerometer:", tuple([ v*self.scale for v in rawVals ]))


class MagnetometerSensorMovementSensorMPU9250(MovementSensorMPU9250SubService):
    def __init__(self):
        super().__init__()
        self.bits = MovementSensorMPU9250.MAG_XYZ
        self.scale = 4912.0 / 32760
        # Reference: MPU-9250 register map v1.4

    def cb_sensor(self, data):
        global mag_value
        '''Returns (x_mag, y_mag, z_mag) in units of uT'''
        rawVals = data[6:9]
        #print("[MovementSensor] Magnetometer:", tuple([ v*self.scale for v in rawVals ]))
        mag_value = data[6]*self.scale
        indicator.append(rawVals)


class GyroscopeSensorMovementSensorMPU9250(MovementSensorMPU9250SubService):
    def __init__(self):
        super().__init__()
        self.bits = MovementSensorMPU9250.GYRO_XYZ
        self.scale = 500.0/65536.0

    def cb_sensor(self, data):
        global gyro_z_value
        '''Returns (x_gyro, y_gyro, z_gyro) in units of degrees/sec'''
        rawVals = data[0:3]
        gyro_z_value = data[2]*self.scale

        #print("[MovementSensor] Gyroscope:", tuple([ v*self.scale for v in rawVals ]))


class OpticalSensor(Sensor):
    def __init__(self):
        super().__init__()
        self.data_uuid = "f000aa71-0451-4000-b000-000000000000"
        self.ctrl_uuid = "f000aa72-0451-4000-b000-000000000000"

    def callback(self, sender: int, data: bytearray):
        global light_value
        raw = struct.unpack('<h', data)[0]
        m = raw & 0xFFF
        e = (raw & 0xF000) >> 12
        value = 0.01 * (m << e)
        #print("[OpticalSensor] Reading from light sensor:", value)
        light_value = value

        indicator.append(value)

class HumiditySensor(Sensor):
    def __init__(self):
        super().__init__()
        self.data_uuid = "f000aa21-0451-4000-b000-000000000000"
        self.ctrl_uuid = "f000aa22-0451-4000-b000-000000000000"

    def callback(self, sender: int, data: bytearray):
        (rawT, rawH) = struct.unpack('<HH', data)
        temp = -40.0 + 165.0 * (rawT / 65536.0)
        RH = 100.0 * (rawH/65536.0)
        #print(f"[HumiditySensor] Ambient temp: {temp}; Relative Humidity: {RH}")
        temp_store.append(temp)


class BarometerSensor(Sensor):
    def __init__(self):
        super().__init__()
        self.data_uuid = "f000aa41-0451-4000-b000-000000000000"
        self.ctrl_uuid = "f000aa42-0451-4000-b000-000000000000"

    def callback(self, sender: int, data: bytearray):
        (tL, tM, tH, pL, pM, pH) = struct.unpack('<BBBBBB', data)
        temp = (tH*65536 + tM*256 + tL) / 100.0
        press = (pH*65536 + pM*256 + pL) / 100.0
        #print(f"[BarometerSensor] Ambient temp: {temp}; Pressure Millibars: {press}")


class LEDAndBuzzer(Service):
    """
        Adapted from various sources. Src: https://evothings.com/forum/viewtopic.php?t=1514 and the original TI spec
        from https://processors.wiki.ti.com/index.php/CC2650_SensorTag_User's_Guide#Activating_IO

        Codes:
            1 = red
            2 = green
            3 = red + green
            4 = buzzer
            5 = red + buzzer
            6 = green + buzzer
            7 = all
    """

    def __init__(self):
        super().__init__()
        self.data_uuid = "f000aa65-0451-4000-b000-000000000000"
        self.ctrl_uuid = "f000aa66-0451-4000-b000-000000000000"

    async def notify(self, client, code):
        # enable the config
        write_value = bytearray([0x01])
        await client.write_gatt_char(self.ctrl_uuid, write_value)

        # turn on the red led as stated from the list above using 0x01
        write_value = bytearray([code])
        await client.write_gatt_char(self.data_uuid, write_value)


async def run(address):

    async with BleakClient(address) as client:
        x = await client.is_connected()
        print("Connected: {0}".format(x))

        led_and_buzzer = LEDAndBuzzer()

        light_sensor = OpticalSensor()
        await light_sensor.start_listener(client)

        humidity_sensor = HumiditySensor()
        await humidity_sensor.start_listener(client)

        barometer_sensor = BarometerSensor()
        await barometer_sensor.start_listener(client)

        acc_sensor = AccelerometerSensorMovementSensorMPU9250()
        gyro_sensor = GyroscopeSensorMovementSensorMPU9250()
        magneto_sensor = MagnetometerSensorMovementSensorMPU9250()

        movement_sensor = MovementSensorMPU9250()
        movement_sensor.register(acc_sensor)
        movement_sensor.register(gyro_sensor)
        movement_sensor.register(magneto_sensor)
        await movement_sensor.start_listener(client)

        cntr = 0
        img_number = 0
        while True:
            # we don't want to exit the "with" block initiating the client object as the connection is disconnected
            # unless the object is stored
            await asyncio.sleep(1.0)
            #print("COUNTER:        ", cntr)

            if cntr == 0:
                # shine the red light
                await led_and_buzzer.notify(client, 0x01)

            if cntr%20 == 0:

                # shine the green light
               # print("GPOMG TP CAMEEFERGE")
                #print(temp_store)
                #camera.click_save_picture(indicator)
                await led_and_buzzer.notify(client, 0x02)
                cntr = 0

            cntr += 1

            #global light_value
            #global mag_value
            global gyro_z_value
            global scam
            fruit = "It is orange!"
            #gyro_bool = gyro_z_door(gyro_z_value)
            #mag_bool = mag_door(mag_value)
            if (gyro_z_door(gyro_z_value)):
            #if(mag_door(mag_value)):
                print("Door just closed.. Lights, Camera, Action!")
                camera.click_save_picture(img_number)
                print("Photo clicked and saved...")
                print("Prediciting which item it is...")
                time.sleep(8)
                if(scam):
                    print("It is grapes!")
                else:
                    print("It is orange!")
                scam = True
                #print(fruit)
                #fruit = "It is grapes!"
                img_number += 1

            #if cntr == 20

def light_door(light_value):
    global light_just_opened
    light_just_closed = False
    if (light_value >= 22):
        light_just_opened = True
    if (light_value <20):
        if (light_just_opened == True):
            light_just_closed = True
            light_just_opened = False
    return light_just_closed

def gyro_z_door(gyro_z_value):
    global gyro_z_just_opened
    global gyro_z_first_confo
    gyro_z_just_closed = False
    if (gyro_z_value >=10):
        gyro_z_just_opened = True
        print ("Door is open...")
    if (gyro_z_value < -10):
        gyro_z_first_confo = True
    if (gyro_z_just_opened and gyro_z_first_confo and gyro_z_value >=0):
        gyro_z_just_closed= True
        gyro_z_just_opened = False
        gyro_z_first_confo = False
    return gyro_z_just_closed

def mag_door(mag_value):
    global mag_just_opened
    mag_just_closed = False
    if (mag_value < 0):
        mag_just_opened = True
    if (mag_value > 0):
        if (mag_just_opened == True):
            mag_just_closed = True
            mag_just_opened = False
    return mag_just_closed

if __name__ == "__main__":
    """
    To find the address, once your sensor tag is blinking the green led after pressing the button, run the discover.py
    file which was provided as an example from bleak to identify the sensor tag device
    """

    import os

    os.environ["PYTHONASYNCIODEBUG"] = str(1)
    address = (
        "54:6C:0E:B5:57:04"
        if platform.system() != "Darwin"
        else "A15BB875-6116-4922-BF97-2464B32FB327"
    )
    indicator = []
    temp_store = []
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(address))
    loop.run_forever()
