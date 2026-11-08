from machine import Pin, time_pulse_us, PWM
from time import sleep, sleep_us, ticks_ms, ticks_diff

# --- Configuration Settings ---
turn_speed = 0      # Speed percentage when steering
speed = 75          # Base speed
turn_time = 0.2
wallturntime = 0.1

left_trim = 1.2     
right_trim = 0.95     

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
echo_1 = Pin(11, Pin.IN)

trigger_2 = Pin(12, Pin.OUT)
echo_2 = Pin(13, Pin.IN)

trigger_1.value(0)
trigger_2.value(0)

def set_speed_percent(enable_pwm, percent, trim=1.0):
    adjusted_percent = max(0, min(100, percent * trim))
    duty = int(adjusted_percent * 65535 / 100)
    enable_pwm.duty_u16(duty)

def read_distance_cm(trigger, echo):
    trigger.value(0)
    sleep_us(2)
    trigger.value(1)
    sleep_us(10)
    trigger.value(0)
    pulse_us = time_pulse_us(echo, 1, 30000)
    if pulse_us < 0:
        return 9999999999
    return pulse_us * 0.0343 / 2

# --- Direction Control Functions ---
def forward():
    left_in1.value(1)
    left_in2.value(0)
    right_in3.value(1)
    right_in4.value(0)

def reverse():
    left_in1.value(0)  
    left_in2.value(1)
    right_in3.value(0)  
    right_in4.value(1)

def pivot_right():
    left_in1.value(1)
    left_in2.value(0)
    right_in3.value(0)
    right_in4.value(1)

def pivot_left():
    left_in1.value(0)
    left_in2.value(1)
    right_in3.value(1)
    right_in4.value(0)

def stop():
    left_in1.value(0)
    left_in2.value(0)
    right_in3.value(0)
    right_in4.value(0)

# Initialize speeds with trim and start driving in reverse
set_speed_percent(left_enable, speed, left_trim)
set_speed_percent(right_enable, speed, right_trim)
reverse()

try:
    while True:
        led.toggle()
        left = left_ir.value()
        right = right_ir.value()
        
        # --- Reverse Line Following Logic ---
        if right == 1 and left == 0:
            set_speed_percent(left_enable, turn_speed, left_trim)
            sleep(turn_time)
            pivot_left()
            set_speed_percent(left_enable, speed, left_trim)
                
        elif left == 1 and right == 0:
            set_speed_percent(right_enable, turn_speed, right_trim)
            sleep(turn_time)
            pivot_right()
            set_speed_percent(right_enable, speed, right_trim)
            
        else:
            set_speed_percent(left_enable, speed, left_trim)
            set_speed_percent(right_enable, speed, right_trim)
            reverse()
        
        # --- Obstacle Avoidance ---
        distance_1 = read_distance_cm(trigger_1, echo_1)
        distance_2 = read_distance_cm(trigger_2, echo_2)
        
        # Uncomment if you want wall avoidance active
        # if distance_1 < 12 and distance_2 < 12:
        #     stop()
        #     pivot_right()
        #     while left_ir.value() != 1 and right_ir.value() != 1:
        #         sleep(0.01)
        #     if wallturntime > 0:
        #         sleep(wallturntime)

        # Your custom loop delay and stopping structure
        sleep_us(100)
        stop()
        sleep_us(100000)

except KeyboardInterrupt:
    stop()