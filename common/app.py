import logger # Added by Pythings

#---------------------
#  Worker task
#---------------------

class worker_task(object):
    
    def __init__(self, chronos):
        logger.info('Initializing user worker task')
    
    def call(self, chronos):
        logger.info ('Called user data_taking {}'.format(chronos.epoch_s()))

#---------------------
#  Management task
#---------------------

class management_task(object):

    def __init__(self, chronos):
        logger.info('Initializing user management task')
    
    def call(self, chronos, data):
        logger.info('Called user remote_mgmt {}'.format(chronos.epoch_s()), data)

 

version='0' # Added by Pythings