from machine import Pin, PWM
from time import sleep, sleep_us


left_enable = PWM(Pin(4))
right_enable = PWM(Pin(8))

left_enable.freq(1000)
right_enable.freq(1000)
left_in1 = Pin(2, Pin.OUT)
left_in2 = Pin(3, Pin.OUT)
right_in3 = Pin(6, Pin.OUT)
right_in4 = Pin(7, Pin.OUT)
# Approximately 50% duty cycle
left_enable.duty_u16(60000)
right_enable.duty_u16(60000)

right_in3.value(1)
right_in4.value(0)

