import machine
LED = machine.Pin(2, machine.Pin.OUT)

def on():
    LED.low()

def off():
    LED.high()
