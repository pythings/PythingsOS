import logger

def handle(e):
    # Do not move the following import on top or code will fail (why?!)
    import sal
    logger.error('Error in executing Pythings OS: "{}". Will report and rebot.'.format(e))
    logger.debug(sal.get_traceback(e))
    try:
        from api import report
        report(what='pythings', status='KO', message='{} {} ({})'.format(e.__class__.__name__, e, sal.get_traceback(e)))
    except Exception as e2:
        logger.error('Could not report error to Pythings Cloud: "{}"'.format(e2))
        logger.debug(sal.get_traceback(e2))
    import time
    time.sleep(1)
    logger.info('I will reboot in 5 seconds. CTRL-C now to stop the reboot.')
    time.sleep(5)
    import hal
    hal.reboot()
