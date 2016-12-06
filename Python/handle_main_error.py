import hal
import time

def handle(e):
    print('Error in executing Pythings framework: ',type(e), str(e))
    import traceback
    hal.print_exception(e)
    try:
        from api import report
        report('pythings', 'KO', e.__class__.__name__+' '+str(e))
    except Exception as e2:
        print('Error in reporting error to Pythings framework: ',type(e2), str(e2))
        hal.print_exception(e2) # TODO: try except also the prints as they can fail due to uncode
        traceback.print_exc()  
    print('\n{}: I will reboot in 5 seconds. CTRL-C now to stop the reboot.'.format(e.__class__.__name__)) 
    
    time.sleep(5)
    hal.reboot()