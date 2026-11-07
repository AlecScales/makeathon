from machine import Pin
from time import sleep

left_ir = Pin(16, Pin.IN)
right_ir = Pin(17, Pin.IN)

while True:
    left = left_ir.value()
    right = right_ir.value()

    print("Left:", left, "Right:", right)
    sleep(0.5)