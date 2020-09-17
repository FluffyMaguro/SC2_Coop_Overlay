import datetime
import traceback

class logclass:
    """ Custom class for logging purposes """
    LOGGING = False
    LEVELS = ['DEBUG','INFO','WARNING','ERROR']
    FILE = "Logging.txt"
    
    def __init__(self,name,level,showtype=True,showdate=True):
        self.name = name
        self.showtype = showtype
        self.level = level
        self.showdate = showdate

        if not(level in self.LEVELS):
            raise Exception(f'logging level has to be in {self.LEVELS}')

    def printsave(self,mtype,message):
        time = datetime.datetime.now().strftime("%H:%M:%S") if self.showdate else ''
        ctype = mtype if self.showtype else ''
        msg = f'{time} - {self.name} ({ctype}): {message}'
        try:
            print(msg)
        except:
            print(traceback.format_exc())

        if self.LOGGING:
            with open(self.FILE,'ab') as f:
                f.write(f'{msg}\n'.encode())

    def debug(self,message):
        if self.level in self.LEVELS[1:]:
            return
        mtype = 'debug'
        self.printsave(mtype,message)

    def info(self,message):
        if self.level in self.LEVELS[2:]:
            return
        mtype = 'info'
        self.printsave(mtype,message)

    def warning(self,message):
        if self.level in self.LEVELS[3:]:
            return
        mtype = 'warning'
        self.printsave(mtype,message)

    def error(self,message):
        mtype = 'ERROR'
        self.printsave(mtype,message)
