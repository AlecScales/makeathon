from machine import Pin, time_pulse_us
from time import sleep, sleep_us

trigger_1 = Pin(12, Pin.OUT)
echo_1 = Pin(13, Pin.IN)  # Divided Echo only.

trigger_2 = Pin(10, Pin.OUT)
echo_2 = Pin(11, Pin.IN)  # Divided Echo only.

trigger_1.value(0)
trigger_2.value(0)

def read_distance_cm(trigger, echo):
    # Send the short trigger pulse.
    trigger.value(0)
    sleep_us(2)
    trigger.value(1)
    sleep_us(10)
    trigger.value(0)

    # Measure how long Echo remains HIGH, with a timeout.
    pulse_us = time_pulse_us(echo, 1, 30000)
    if pulse_us < 0:
        return None

    # Sound travels to the object and back, so divide by two.u
    return pulse_us * 0.0343 / 2

while True:
    distance_1 = read_distance_cm(trigger_1, echo_1)
    print("Sensor 1:", "No echo" if distance_1 is None else distance_1)

    sleep(0.1)

    distance_2 = read_distance_cm(trigger_2, echo_2)
    print("Sensor 2:", "No echo" if distance_2 is None else distance_2)
    sleep(0.2)