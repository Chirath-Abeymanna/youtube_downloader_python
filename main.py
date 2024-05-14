# CREATOR: C.C

import sys 
import os
from pathlib import Path

#NOTE: Below libraries should be downloaded if not already
#NOTE: pyperclip,PyQt5,pytube

from PyQt5.QtWidgets import QMainWindow,QMessageBox,QFileDialog,QApplication,QLabel,QPushButton,QLineEdit,QComboBox,QFrame 
from PyQt5 import uic,QtGui,QtCore 
from PyQt5.uic import loadUi 
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, QThreadPool,Qt
from pytube import YouTube 
import pyperclip 

from contents import video_converter

 #changing the working directory
working_directory = Path(__file__).absolute().parent

#Function to paste the copied url
def url_paste(widget):
    copied_url = pyperclip.paste()
    widget.clear()
    widget.setText(copied_url)

#Creating objects to multithreading processes
class WorkerSignals(QObject):

    finished = pyqtSignal()
    streams_found = pyqtSignal(object,object)
    update_signal = pyqtSignal()

#Thread pool class to show gif
class WorkerAnimation(QRunnable):
    def __init__(self, signal_emitter):
        super().__init__()
        self.signal_emitter = signal_emitter
        self.signals = WorkerSignals()

    def run(self):

        # Emit signal to update GUI
        self.signal_emitter.update_signal.emit()
        self.signals.finished.emit()

#Thred pool class to find and download videos
class Worker(QRunnable):
    def __init__(self, fun, *args, **kwargs):
        super(Worker, self).__init__()
        self.fun = fun
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self):
        result = self.fun(*self.args, **self.kwargs)
        if result is not None:
            yt, streams = result
            self.signals.streams_found.emit(yt, streams)
        self.signals.finished.emit()

#Downloading video function
def download_video_func(entry,options,window,main_window):
        
        try:

            main_window.progress_label.clear()
            
            print("\n---------Download status-------------------")
            print("Selected URL: ",entry.text())
            print("Selected format: ", options.currentText())

            id = 0
      
            folder =  QFileDialog.getExistingDirectory(window, "Save Location", "", QFileDialog.ShowDirsOnly)
            url = entry.text()

            #Create a global threadpool
            thread_pool = QThreadPool.globalInstance()
            
            # Start loading animation
            signal_emitter = WorkerSignals()
            signal_emitter.update_signal.connect(main_window.loading_animation)
    
            worker2 = WorkerAnimation(signal_emitter)
            thread_pool.start(worker2)

            if options.currentText() == "mp3/audio":

                worker_audio = Worker(finding_streams,options, url, main_window)
                thread_pool.start(worker_audio)  # Submit the worker to the thread pool
                id = 1

                # Get the global QThreadPool instance
                worker_audio.signals.streams_found.connect(lambda yt,streams: handle_streams_found(yt,streams,folder,window,main_window,thread_pool,id))
            
            else:
                # Create an instance of Worker with download_video function and its arguments
                worker = Worker(finding_streams,options, url, main_window)

                thread_pool.start(worker)  # Submit the worker to the thread pool

                # Get the global QThreadPool instance
                worker.signals.streams_found.connect(lambda yt,streams: handle_streams_found(yt,streams,folder,window,main_window,thread_pool,id))

            window.close()

        except Exception as e:
            print("lamba error",e)
            main_window.show_error_message(str(e))
            window.close()

def finding_streams(options,url,main_window):

    try:
            yt =YouTube(url)
            resolution = options.currentText()
            split_resolution = resolution.split("/")
            print("Youtube video title: ",yt.title)
            try:

                if split_resolution[0] == "highest":
                    streams = yt.streams.filter(progressive=True,file_extension="mp4").get_highest_resolution()
                
                elif split_resolution[0] == "mp3":
                    streams = yt.streams.filter(only_audio=True).first()
                
                else:
                    streams = yt.streams.filter(res=f"{split_resolution[0]}",file_extension="mp4").first()
                
                return yt,streams

            except Exception as e:
                print(e)
                main_window.show_error_message(str(e))
                
    except Exception as e:
        print(e)
        main_window.show_error_message(str(e))

#Changing animations when the stream being found
def handle_streams_found(yt,streams,folder,window,main_window,thread_pool,id):

    print("Choosed stream:",streams)

    downloading_animation(main_window,thread_pool)

    if id == 1:

        # Create an instance of Worker with download_video function and its arguments
        worker = Worker(download_audio,yt,streams,folder,main_window,thread_pool)
    else:
        # Create an instance of Worker with download_video function and its arguments
        worker = Worker(download_video,streams,folder,main_window)

    thread_pool.start(worker)  # Submit the worker to the thread pool
    worker.signals.finished.connect(lambda: download_complete(main_window,thread_pool))


def download_audio(yt,audio,folder,main_window,thread_pool):

    try: 

        path = (working_directory/"resources")
        download = audio.download(output_path=path)
        print(download)
        back_slash = "/"
        output_name = f"{folder+back_slash+yt.title}.mp3"
        print(output_name)
        video_converter.convert_to_mp3(download,output_name) 
        os.remove(download)
    
    except Exception as e:
        main_window.show_error_message(str(e))


def download_video(streams,folder,main_window):
            try:
                print ("Starting download ....")
                streams.download(output_path=folder)
                print("Download completed")
                    
            except Exception as e:
                print(e)
                main_window.show_error_message(str(e))


def stop_loading(main_window,thread_pool):

    # Stop loading status gif and start downloading gif         
    signal_emitter = WorkerSignals()
    signal_emitter.update_signal.connect(lambda: download_complete(main_window,thread_pool))

    worker2 = WorkerAnimation(signal_emitter)
    thread_pool.start(worker2)

    main_window.show_info_message()


def downloading_animation(main_window,thread_pool):
        
    main_window.progress_label.clear()

    # Start loading animation
    signal_emitter = WorkerSignals()
    signal_emitter.update_signal.connect(main_window.downloading_animation)
    
    worker = WorkerAnimation(signal_emitter)
    thread_pool.start(worker)


def download_complete(main_window,thread_pool):

    main_window.progress_label.clear()

    # Start loading animation
    signal_emitter = WorkerSignals()
    signal_emitter.update_signal.connect(main_window.download_complete)
    
    worker = WorkerAnimation(signal_emitter)
    thread_pool.start(worker)

    worker.signals.finished.connect(main_window.show_info_message)

class GUI(QMainWindow):
    def __init__(self):
        super(GUI,self).__init__()

        #Making a frameless window
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)

        #Loading GUI
        uic.loadUi( working_directory /"design/main_window.ui",self)

        #getting the widgets
        self.main_window()

        #show the GUI
        self.show()

    def main_window(self):
        
        self.paste_btn = self.findChild(QPushButton,"paste_btn")
        self.download_btn =self.findChild(QPushButton,"download_btn")
        self.url = self.findChild(QLineEdit,"url_entry")
        self.logo = self.findChild(QLabel,"logo")

        self.progress_label = self.findChild(QLabel,"download_ani")

        self.paste_btn.clicked.connect(lambda:url_paste(self.url))

        self.download_btn.clicked.connect(self.open_second_window)

        #Getting the contents in the title bar
        self.title_bar = self.findChild(QFrame,"titleBar")
        self.close_btn = self.findChild(QPushButton,"closeButton")
        self.minimize_btn = self.findChild(QPushButton,"minimizeButton")

        #Making the close and minimize buttons work
        self.close_btn.clicked.connect(self.close_btn_func)
        self.minimize_btn.clicked.connect(self.showMinimized)

        # Initialize second window as None
        self.second_window = None
    
    def open_second_window(self):

        if self.url.text() != "":

            if "youtu" in self.url.text():

                self.progress_label.clear()

                # Check if second_window is already created
                if not self.second_window:
                    # Load the second window from the .ui file
                    self.second_window = loadUi(working_directory/"design/second_window.ui")

                    self.second_window.setWindowFlag(Qt.WindowType.FramelessWindowHint)

                    #Getting the contents in the title bar
                    self.title_bar1 = self.second_window.findChild(QFrame,"titleBar1")
                    self.close_btn1 = self.second_window.findChild(QPushButton,"closeButton")
                    self.minimize_btn1 = self.second_window.findChild(QPushButton,"minimizeButton")

                    #Making the close and minimize buttons work
                    self.close_btn1.clicked.connect(self.second_window.close)
                    self.minimize_btn1.clicked.connect(self.second_window.showMinimized)

                    self.download_video = self.second_window.findChild(QPushButton,"download_btn")
                    self.resolutions = self.second_window.findChild(QComboBox,"resolution_box")

                    self.download_video.clicked.connect(lambda: download_video_func(self.url,self.resolutions,self.second_window,self))
                # Show the second window
                self.second_window.show()
            
            else:
                error = "Invalid URL"
                self.show_error_message(error)

        else:
            error = "No URL in the text box Please provide a URL"
            self.show_error_message(error)
    
    def mousePressEvent(self, event):
        if (event.button() == Qt.LeftButton and self.title_bar.geometry().contains(event.pos())):
            self.offset = event.pos()

        elif event.button() == Qt.LeftButton:
            self.offset = None

        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == QtCore.Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.offset)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.offset = None
        super().mouseReleaseEvent(event)

    #Creating a function to close the windows
    def close_btn_func(self):

        self.close()
        if self.second_window :
            self.second_window.close()
        sys.exit()

    def loading_animation(self):
        
        self.loading_status = QtGui.QMovie("resources/loading.gif")
        self.progress_label.setMovie(self.loading_status)

        # Align the movie to the center of the QLabel
        self.progress_label.setAlignment(QtCore.Qt.AlignCenter)

        self.loading_status.start()
        if self.loading_status.isValid():
            print("loading animation working sucessfully")
        else:
            print("loading animation didn't load suceessfully")
    
    def downloading_animation(self):
        
        self.download_status = QtGui.QMovie("resources/download_start.gif")
        self.progress_label.setMovie(self.download_status)
        self.download_status.start()
        if self.download_status.isValid():
            print("downloading animation working sucessfully")
        else:
            print("downloading animation didn't load suceessfully")

    def download_complete(self):
        self.complete_status = QtGui.QMovie("resources/download_complete.gif")
        self.progress_label.setMovie(self.complete_status)
        self.complete_status.start()
        if self.complete_status.isValid():
            print("download complete animation working sucessfully")
        else:
            print("download complete animation didn't load suceessfully")
   
    def show_error_message(self,error):
        # Create and show an error message box
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Critical)
        error_box.setWindowTitle('Error')
        error_box.setText(error)
        error_box.setStandardButtons(QMessageBox.Ok)
        error_box.exec_()
    
    def show_info_message(self):
        # Create and show an error message box
        info_box = QMessageBox()
        info_box.setIcon(QMessageBox.Information)
        info_box.setWindowTitle('Download status')
        info_box.setText('Video downloaded successfully!')
        info_box.setStandardButtons(QMessageBox.Ok)
        info_box.exec_()
    
     
#Running application
if __name__ =="__main__":

    app = QApplication(sys.argv)
    GUIWindow = GUI()
    app.exec_()

