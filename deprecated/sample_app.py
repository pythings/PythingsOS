#---------------------
#  User tasks
#---------------------

class worker_task(object):
    
    def __init__(self, chronos):
        print('Initializing user data_taking')
    
    def call(self, chronos):
        '''STATELESS. If you need to save temp data between the calls, use a file, NOT memory.
        Acttually, this is handled by pythings itself..
        If output = None, no data is sent at all (and no radio is activated)'''
        print ('Called user data_taking', chronos.epoch_s())
        # TODO: Pythings MUST try-except this call, it crashes the framework now (which is recovered)
        
        import machine
        adc = machine.ADC(0)
        luminosity = adc.read()
        
        import time
        LED = machine.Pin(2, machine.Pin.OUT)
        LED.low()
        time.sleep(0.25)
        LED.high()
        
        import network
        wlan = network.WLAN(network.STA_IF)
        nets = wlan.scan()
        signal = None
        for net in nets:
            signal = net[3]
        
        data = {'signal_dBm': signal, 'luminosity_au':luminosity}
        return data

class management_task(object):

    def __init__(self, chronos):
        print('Initializing user remote_mgmt')
    
    def call(self, chronos, data):
        print ('Called user remote_mgmt', chronos.epoch_s(), data)
        
worker_interval=60
management_interval=5
    
