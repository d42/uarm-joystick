import evdev
from pyuarm import UArm
from pyuarm.protocol import SERVO_BOTTOM, SERVO_RIGHT, SERVO_LEFT, SERVO_HAND
from time import sleep
from evdev import ecodes
from random import randint
from asyncore import file_dispatcher, loop
import sys

j = evdev.InputDevice(sys.argv[1])


class InputDeviceDispatcher(file_dispatcher):
    x_mid = 70
    y_mid = 50
    deadzone = 8

    def __init__(self, device, uarm):
        self.device = device
        self.uarm = uarm
        file_dispatcher.__init__(self, device)

    def recv(self, ign=None):
        return self.device.read()

    def move_arm(self, event):
        direction = {
            ecodes.ABS_X: SERVO_BOTTOM,
            ecodes.ABS_Y: SERVO_LEFT,
            ecodes.ABS_THROTTLE: SERVO_RIGHT,
            ecodes.ABS_HAT0X: SERVO_HAND
        }[event.code]

        self.uarm.set_servo_angle(direction, event.value)

    def suck(self):
        self.uarm.set_pump(True)

    def dont_suck(self):
        self.uarm.set_pump(False)

    def buzz(self, h):
        self.uarm.set_buzzer(h, 1)

    def handle_read(self):
        for event in self.recv():
            if event.code == ecodes.ABS_X and event.value == 0:
                continue
            if event.code == ecodes.ABS_THROTTLE:
                self.move_arm(event)

            elif event.code == ecodes.ABS_X:
                event.value = 160 - event.value
                self.move_arm(event)

            elif event.code == ecodes.ABS_Y:
                event.value = event.value
                self.move_arm(event)

            elif event.code == ecodes.BTN_TRIGGER:
                self.suck() if event.value else self.dont_suck()

            elif event.code == ecodes.BTN_TOP:
                if event.value:
                    self.buzz(randint(20, 400))
            elif event.code == ecodes.ABS_HAT0X:
                event.value = (event.value+1) * 90
                self.move_arm(event)
            else:
                print(evdev.categorize(event), event)


class GuwnoArm(UArm):

    def is_ready(self):
        sleep(4)
        self._UArm__isConnected = True
        return True


InputDeviceDispatcher(j, GuwnoArm(sys.argv[2], debug=True))
loop()
