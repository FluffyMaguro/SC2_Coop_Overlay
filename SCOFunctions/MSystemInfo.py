import psutil
import traceback
from PyQt5 import QtCore, QtGui, QtWidgets

from SCOFunctions.MFilePath import innerPath
from SCOFunctions.MLogging import logclass

logger = logclass('SYS','INFO')


class SystemInfo(QtWidgets.QWidget):
    """ This widget overlays system and StarCraft II information on-screen (CPU, RAM, Disk, Network,...) """
    def __init__(self, geometry=None, process_names=None, parent=None):
        super().__init__(parent)

        if geometry == None:
            self.setGeometry(0, 0, 260, 400)
            sg = QtWidgets.QDesktopWidget().screenGeometry(0)
            self.move(sg.width()-self.width()-10, sg.top()+210)
        else:
            self.setGeometry(*geometry)
        
        self.setWindowTitle('Performance overaly position')
        self.setWindowIcon(QtGui.QIcon(innerPath('src/OverlayIcon.ico')))

        # Move to top-right

        self.setStyleSheet('color: white')

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint|QtCore.Qt.WindowTransparentForInput|QtCore.Qt.WindowStaysOnTopHint|QtCore.Qt.CoverWindow|QtCore.Qt.NoDropShadowWindowHint|QtCore.Qt.WindowDoesNotAcceptFocus)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

        # Data
        self.restart() # Inits some data
        self.core_count = psutil.cpu_count()
        self.iter = 1000 # Length of whole loop in miliseconds
        self.sc2process_names = process_names
        self.fixed = True
        self.started = False
        self.bytes_sent = None
        self.bytes_recv = None

        # SC2 widgets
        self.layout = QtWidgets.QGridLayout()
        self.layout.setAlignment(QtCore.Qt.AlignTop)
        self.layout.setVerticalSpacing(2)
        self.setLayout(self.layout)

        self.la_sc2 = QtWidgets.QLabel()
        self.la_sc2.setText('<b>StarCraft II</b>')
        self.layout.addWidget(self.la_sc2, 0, 0, 1, 2)

        self.la_sc2_memory = QtWidgets.QLabel()
        self.la_sc2_memory.setText('RAM')
        self.layout.addWidget(self.la_sc2_memory, 1, 0, 1, 1)

        self.la_sc2_memory_value = QtWidgets.QLabel()
        self.layout.addWidget(self.la_sc2_memory_value, 1, 1, 1, 1)

        self.la_sc2_read = QtWidgets.QLabel()
        self.la_sc2_read.setText('Read')
        self.layout.addWidget(self.la_sc2_read, 2, 0, 1, 1)

        self.la_sc2_read_value = QtWidgets.QLabel()
        self.layout.addWidget(self.la_sc2_read_value, 2, 1, 1, 1)

        self.la_sc2_read_value_total = QtWidgets.QLabel()
        self.layout.addWidget(self.la_sc2_read_value_total, 3, 1, 1, 1)

        self.la_sc2_write = QtWidgets.QLabel()
        self.la_sc2_write.setText('Write')
        self.layout.addWidget(self.la_sc2_write, 4, 0, 1, 1)

        self.la_sc2_write_value = QtWidgets.QLabel()
        self.layout.addWidget(self.la_sc2_write_value, 4, 1, 1, 1)

        self.la_sc2_write_value_total = QtWidgets.QLabel()
        self.layout.addWidget(self.la_sc2_write_value_total, 5, 1, 1, 1)

        self.la_spacer = QtWidgets.QLabel()
        self.la_spacer.setText('')
        self.layout.addWidget(self.la_spacer, 6, 0, 1, 1)

        self.la_sc2_cpu = QtWidgets.QLabel()
        self.la_sc2_cpu.setText('<b>CPUc</b>')
        self.layout.addWidget(self.la_sc2_cpu, 7, 0, 1, 1)

        self.la_sc2_cpu_value = QtWidgets.QLabel()
        self.layout.addWidget(self.la_sc2_cpu_value, 7, 1, 1, 1)

        # System widgets
        self.la_system = QtWidgets.QLabel()
        self.la_system.setText('<b>System</b>')
        self.layout.addWidget(self.la_system, 0, 2, 1, 2)

        self.la_memory = QtWidgets.QLabel()
        self.la_memory.setText('RAM')
        self.layout.addWidget(self.la_memory, 1, 2, 1, 1)

        self.la_memory_value = QtWidgets.QLabel()
        self.layout.addWidget(self.la_memory_value, 1, 3, 1, 1)

        self.la_download = QtWidgets.QLabel()
        self.la_download.setText('Down')
        self.layout.addWidget(self.la_download, 2, 2, 1, 1)

        self.la_download_value = QtWidgets.QLabel()
        self.layout.addWidget(self.la_download_value, 2, 3, 1, 1)

        self.la_download_value_total = QtWidgets.QLabel()
        self.layout.addWidget(self.la_download_value_total, 3, 3, 1, 1)

        self.la_upload = QtWidgets.QLabel()
        self.la_upload.setText('Upload')
        self.layout.addWidget(self.la_upload, 4, 2, 1, 1)

        self.la_upload_value = QtWidgets.QLabel()
        self.layout.addWidget(self.la_upload_value, 4, 3, 1, 1)

        self.la_upload_value_total = QtWidgets.QLabel()
        self.layout.addWidget(self.la_upload_value_total, 5, 3, 1, 1)

        self.la_cpu = QtWidgets.QLabel()
        self.la_cpu.setText('<b>CPU utilization</b>')
        self.layout.addWidget(self.la_cpu, 7, 2, 1, 2)

        self.cpu_cores = dict()
        for idx in range(psutil.cpu_count()):
            self.cpu_cores[('label', idx)] = QtWidgets.QLabel()
            self.cpu_cores[('label', idx)].setText(f"CPU{idx}")
            self.cpu_cores[('label', idx)].setAlignment(QtCore.Qt.AlignRight)
            self.layout.addWidget(self.cpu_cores[('label', idx)], 8 + idx, 2, 1, 1)

            self.cpu_cores[('value', idx)] = QtWidgets.QLabel()
            self.cpu_cores[('value', idx)].setAlignment(QtCore.Qt.AlignLeft)
            self.layout.addWidget(self.cpu_cores[('value', idx)], 8 + idx, 3, 1, 1)


        self.cpu_cores['total_label'] = QtWidgets.QLabel()
        self.cpu_cores['total_label'].setAlignment(QtCore.Qt.AlignRight)
        self.cpu_cores['total_label'].setText('total')
        self.layout.addWidget(self.cpu_cores['total_label'], 8 + idx + 1, 2, 1, 1)

        self.cpu_cores['total'] = QtWidgets.QLabel()
        self.cpu_cores['total'].setAlignment(QtCore.Qt.AlignLeft)
        self.layout.addWidget(self.cpu_cores['total'], 8 + idx + 1, 3, 1, 1)

        # Headers
        headers = {self.la_sc2, self.la_system, self.la_cpu}
        for item in headers:
            item.setAlignment(QtCore.Qt.AlignCenter)

        # Labels
        labels = {self.la_upload, self.la_download, self.la_memory, self.la_sc2_read, self.la_sc2_write, self.la_sc2_cpu, self.la_sc2_memory}
        for item in labels:
            item.setAlignment(QtCore.Qt.AlignRight)

        # Values
        values = {self.la_download_value_total, self.la_upload_value_total, self.la_sc2_read_value_total, self.la_sc2_write_value_total, self.la_upload_value, self.la_download_value, self.la_memory_value, self.la_sc2_read_value, self.la_sc2_write_value, self.la_sc2_cpu_value, self.la_sc2_memory_value}
        for item in values:
            item.setAlignment(QtCore.Qt.AlignLeft)

        # Add shadows to everything
        for item in headers.union(labels).union(values).union({self.cpu_cores[i] for i in self.cpu_cores}):
            shadow = QtWidgets.QGraphicsDropShadowEffect() 
            shadow.setBlurRadius(3)
            shadow.setOffset(1)
            shadow.setColor(QtGui.QColor(0, 0, 0))
            item.setGraphicsEffect(shadow)     


    def start(self):
        """ Periodic update """
        self.started = True
        self.show()
        self.Timer = QtCore.QTimer()
        self.Timer.setInterval(self.iter)
        self.Timer.timeout.connect(self.update)
        self.Timer.start()
        

    def restart(self):
        """ Defaults some variables """
        self.sc2_pid = None
        self.sc2_bytes_read = None
        self.sc2_bytes_written = None
        self.sc2_process = None
        

    def update(self):
        # Network up and down
        network_data = psutil.net_io_counters()
        if self.bytes_sent != None and self.bytes_recv != None:
            sent = (1000/self.iter)*(network_data.bytes_sent - self.bytes_sent)
            recv = (1000/self.iter)*(network_data.bytes_recv - self.bytes_recv)
            self.la_download_value.setText(f"{self.format_bytes(recv)}/s")
            self.la_upload_value.setText(f"{self.format_bytes(sent)}/s")           

        self.bytes_sent = network_data.bytes_sent
        self.bytes_recv = network_data.bytes_recv

        self.la_download_value_total.setText(self.format_bytes(self.bytes_recv))
        self.la_upload_value_total.setText(self.format_bytes(self.bytes_sent))

        # CPU
        cpu_percent = psutil.cpu_percent(percpu=True, interval=0)
        for idx, cpu in enumerate(cpu_percent):
            self.cpu_cores[('value', idx)].setText(f'{cpu}%')
            if cpu > 85:
                self.cpu_cores[('value', idx)].setStyleSheet('color:#FF8787')
            elif cpu < 15:
                self.cpu_cores[('value', idx)].setStyleSheet('color: rgba(255,255,255,0.5)')
            else:
                self.cpu_cores[('value', idx)].setStyleSheet('color:white')

        self.cpu_cores['total'].setText(f"{psutil.cpu_percent():.1f}%")

        # RAM
        memory = psutil.virtual_memory()
        self.la_memory_value.setText(f"{memory.used/1024**3:.1f}/{memory.total/1024**3:.1f} GB")
        if memory.percent > 90:
            self.la_memory_value.setStyleSheet('color:red')
        else:
            self.la_memory_value.setStyleSheet('color:white')


        # Get StarCraft 2 process if there is none
        if self.sc2_process == None:
            try:
                for pid in psutil.pids():
                    process = psutil.Process(pid)
                    if process.name() in self.sc2process_names:
                        self.sc2_pid = pid
                        self.sc2_process = psutil.Process(self.sc2_pid)
                        break
            except:
                self.restart()
                return                
        
        # We haven't found StarCraft process running
        if self.sc2_process == None:
            self.restart()
            return 

        # Use cached values of the process
        with self.sc2_process.oneshot():
            if 'SC2' in self.sc2_process.name():
                self.la_sc2.setText('<b>StarCraft II</b>')
            else:
                self.la_sc2.setText(f"<b>{self.sc2_process.name()}</b>")

            try:
                # Disk usage
                if self.sc2_bytes_read != None:
                    read = (1/self.iter)*(self.sc2_process.io_counters().read_bytes - self.sc2_bytes_read)
                    writen = (1/self.iter)*(self.sc2_process.io_counters().write_bytes -self.sc2_bytes_written)
                    self.la_sc2_read_value.setText(f"{self.format_bytes(read)}/s")
                    self.la_sc2_write_value.setText(f"{self.format_bytes(writen)}/s")

                self.sc2_bytes_read = self.sc2_process.io_counters().read_bytes
                self.sc2_bytes_written = self.sc2_process.io_counters().write_bytes

                self.la_sc2_read_value_total.setText(f"{self.format_bytes(self.sc2_bytes_read)}")
                self.la_sc2_write_value_total.setText(f"{self.format_bytes(self.sc2_bytes_written)}")

                # CPU
                self.la_sc2_cpu_value.setText(f"{self.sc2_process.cpu_percent()}%")
                # RAM
                self.la_sc2_memory_value.setText(f"{self.sc2_process.memory_percent():.0f}% | {self.sc2_process.memory_info().rss/1024/1024:.0f} MB")

            except psutil.NoSuchProcess:
                # Set no values
                self.restart()
                for item in {self.la_sc2_read_value_total, self.la_sc2_write_value_total, self.la_sc2_read_value, self.la_sc2_write_value, self.la_sc2_cpu_value, self.la_sc2_memory_value}:
                    item.setText('')
            except:
                logger.error(traceback.format_exc())


    @staticmethod
    def format_bytes(bbytes: int) -> str:
        """ Takes bytes and outputs a string 'X kB' or 'Y MB' or 'Z GB' """
        if bbytes < 0.3*1024**2:
            return f'{bbytes/1024:.1f} kB'
        elif bbytes < 0.7*1024**3:
            return f'{bbytes/1024**2:.1f} MB'
        else:
            return f'{bbytes/1024**3:.1f} GB'
