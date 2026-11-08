from machine import Pin, time_pulse_us, PWM
from time import sleep_us, sleep_ms, ticks_ms, ticks_diff

# --- Configuration ---
SPEED        = 80      # straight-line speed (%)
TURN_POWER   = 80      # speed while pivoting (%)
LEFT_TRIM    = 1
RIGHT_TRIM   = 1

PULSE_MODE   = True   # True = old drive/pause pulsing (slow, careful)
DRIVE_MS     = 100
PAUSE_MS     = 100000

CORNER_NUDGE_MS = 0    # keep driving this long before pivoting, so the
                       # wheel axle reaches the corner (try 30-120)
MIN_TURN_MS  = 60      # ignore the sensors for this long at turn start
MAX_TURN_MS  = 1500    # safety timeout for a turn
SETTLE_READS = 3       # consecutive "centred" reads needed to finish turn

WALL_AVOID   = False
WALL_CM      = 12

# --- Pins ---
left_in1, left_in2 = Pin(2, Pin.OUT), Pin(3, Pin.OUT)
right_in3, right_in4 = Pin(6, Pin.OUT), Pin(7, Pin.OUT)
led = Pin(25, Pin.OUT)

left_enable = PWM(Pin(4));  left_enable.freq(1000)
right_enable = PWM(Pin(8)); right_enable.freq(1000)

left_ir, right_ir = Pin(16, Pin.IN), Pin(17, Pin.IN)

trigger_1, echo_1 = Pin(10, Pin.OUT), Pin(11, Pin.IN)
trigger_2, echo_2 = Pin(12, Pin.OUT), Pin(13, Pin.IN)
trigger_1.value(0)
trigger_2.value(0)

# --- Helpers ---
def set_speed_percent(pwm, percent, trim=1.0):
    p = max(0, min(100, percent * trim))
    pwm.duty_u16(int(p * 65535 / 100))

def set_speeds(percent):
    set_speed_percent(left_enable, percent, LEFT_TRIM)
    set_speed_percent(right_enable, percent, RIGHT_TRIM)

def read_distance_cm(trigger, echo):
    trigger.value(0)
    sleep_us(2)
    trigger.value(1)
    sleep_us(10)
    trigger.value(0)
    pulse_us = time_pulse_us(echo, 1, 30000)
    if pulse_us < 0:
        return 9999
    return pulse_us * 0.0343 / 2

# --- Direction control ---
def forward():
    left_in1.value(1); left_in2.value(0)
    right_in3.value(1); right_in4.value(0)

def reverse():
    left_in1.value(0); left_in2.value(1)
    right_in3.value(0); right_in4.value(1)

def pivot_right():
    left_in1.value(1); left_in2.value(0)
    right_in3.value(0); right_in4.value(1)

def pivot_left():
    left_in1.value(0); left_in2.value(1)
    right_in3.value(1); right_in4.value(0)

def stop():
    left_in1.value(0); left_in2.value(0)
    right_in3.value(0); right_in4.value(0)

# --- 90-degree turn ---
def do_turn(pivot_fn):
    """Pivot until the line is back between the two sensors."""
    if CORNER_NUDGE_MS > 0:
        set_speeds(SPEED)
        reverse()
        sleep_ms(CORNER_NUDGE_MS)

    set_speeds(TURN_POWER)
    pivot_fn()

    start = ticks_ms()
    centred = 0
    while ticks_diff(ticks_ms(), start) < MAX_TURN_MS:
        led.toggle()
        if ticks_diff(ticks_ms(), start) > MIN_TURN_MS:
            if left_ir.value() == 0 and right_ir.value() == 0:
                centred += 1
                if centred >= SETTLE_READS:
                    break
            else:
                centred = 0
        sleep_ms(1)

    stop()
    set_speeds(SPEED)

# --- Main loop ---
set_speeds(SPEED)
reverse()

try:
    while True:
        led.toggle()
        left = left_ir.value()
        right = right_ir.value()

        # Obstacle check (only if enabled)
        if WALL_AVOID:
            d1 = read_distance_cm(trigger_1, echo_1)
            d2 = read_distance_cm(trigger_2, echo_2)
            if d1 < WALL_CM and d2 < WALL_CM:
                stop()
                do_turn(pivot_right)
                continue

        if right == 1 and left == 0:       # corner/line on right sensor
            do_turn(pivot_left)
            reverse()
        elif left == 1 and right == 0:     # corner/line on left sensor
            do_turn(pivot_right)
            reverse()
        else:                              # centred (0,0) or junction (1,1)
            set_speeds(SPEED)
            reverse()

        if PULSE_MODE:
            sleep_ms(DRIVE_MS)
            stop()
            sleep_ms(PAUSE_MS)
        else:
            sleep_ms(1)

except KeyboardInterrupt:
    stop()
    set_speeds(0)