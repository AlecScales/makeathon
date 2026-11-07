from machine import Pin, time_pulse_us, PWM
from time import sleep, sleep_us

# --- Configuration Settings ---
turn_speed = 50      # Speed percentage when steering away from an edge
speed = 100
turn_time = 0.05

# --- Pin Pinout Configurations ---
left_in1 = Pin(2, Pin.OUT)
left_in2 = Pin(3, Pin.OUT)
right_in3 = Pin(6, Pin.OUT)
right_in4 = Pin(7, Pin.OUT)
led = Pin(25, Pin.OUT)

left_enable = PWM(Pin(4))
left_enable.freq(1000)
right_enable = PWM(Pin(8))
right_enable.freq(1000)

left_ir = Pin(16, Pin.IN)
right_ir = Pin(17, Pin.IN)

trigger_1 = Pin(10, Pin.OUT)
echo_1 = Pin(11, Pin.IN)  # Divided Echo only.

trigger_2 = Pin(12, Pin.OUT)
echo_2 = Pin(13, Pin.IN)  # Divided Echo only.

# Initialize ultrasonic triggers to LOW
trigger_1.value(0)
trigger_2.value(0)

def set_speed_percent(enable_pwm, percent):
    percent = max(0, min(100, percent))
    duty = int(percent * 65535 / 100)
    enable_pwm.duty_u16(duty)

def read_distance_cm(trigger, echo):
    trigger.value(0)
    sleep_us(2)
    trigger.value(1)
    sleep_us(10)
    trigger.value(0)
    pulse_us = time_pulse_us(echo, 1, 30000)
    if pulse_us < 0:
        return None
    return pulse_us * 0.0343 / 2

# --- Direction Control Functions ---
def forward():
    left_in1.value(1)
    left_in2.value(0)
    right_in3.value(1)
    right_in4.value(0)

def reverse():
    left_in1.value(0)  # Inverted from forward
    left_in2.value(1)
    right_in3.value(0)  # Inverted from forward
    right_in4.value(1)

def leftonly():
    left_in1.value(1)
    left_in2.value(0)

def rightonly():
    right_in3.value(1)
    right_in4.value(0)

def leftstop():
    left_in1.value(0)
    left_in2.value(0)

def rightstop():
    right_in3.value(0)
    right_in4.value(0)

def stop():
    left_in1.value(0)
    left_in2.value(0)
    right_in3.value(0)
    right_in4.value(0)




set_speed_percent(left_enable, speed)
set_speed_percent(right_enable, speed)
forward()
try:
    while True:
        led.toggle()
        
        # Read digital line sensors
        left = left_ir.value()
        right = right_ir.value()
        
        if left == 1 and right == 0:
            set_speed_percent(left_enable, turn_speed)
            sleep(turn_time)
            set_speed_percent(left_enable, speed)
            
        elif right == 1 and left == 0:
            set_speed_percent(right_enable, turn_speed)
            sleep(turn_time)
            set_speed_percent(right_enable, speed)
            
        else:
            set_speed_percent(left_enable, speed)
            set_speed_percent(right_enable, speed)
        
        distance_1 = read_distance_cm(trigger_1, echo_1)
        
        sleep_us(100)

except KeyboardInterrupt:
    stop()
