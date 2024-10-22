# CREATOR: C.C

import sys 
import os
import shutil
import re

#NOTE: Below libraries should be downloaded if not already
#NOTE: pyperclip,PyQt5,pytube

from PyQt5.QtWidgets import QMainWindow,QMessageBox,QFileDialog,QApplication,QLabel,QPushButton,QLineEdit,QComboBox,QFrame 
from PyQt5 import uic,QtGui,QtCore 
from PyQt5.uic import loadUi 
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, QThreadPool,Qt
from pytube import YouTube 
import pyperclip 

from contents import video_converter

#Creating a resourcepath function
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

#Function to paste the copied url
def url_paste(widget):
    copied_url = pyperclip.paste()
    widget.clear()
    widget.setText(copied_url)

    #deiojfwefoi

#Creating objects to multithreading processes
class WorkerSignals(QObject):

    finished = pyqtSignal()
    streams_found = pyqtSignal(object,object,object,object)
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
            yt, streams,stream_audio,status = result
            self.signals.streams_found.emit(yt, streams,stream_audio,status)
        self.signals.finished.emit()

#Downloading video function
def download_video_func(entry,options,window,main_window):
        
        try:

            main_window.progress_label.clear()
            
      
            folder =  QFileDialog.getExistingDirectory(window, "Save Location", "", QFileDialog.ShowDirsOnly)
            url = entry.text()

            if folder:

                print("\n---------Download status-------------------")
                print("Selected URL: ",entry.text())
                print("Selected format: ", options.currentText())

                #Create a global threadpool
                thread_pool = QThreadPool.globalInstance()
                
                # Start loading animation
                signal_emitter = WorkerSignals()
                signal_emitter.update_signal.connect(main_window.loading_animation)
        
                worker2 = WorkerAnimation(signal_emitter)
                thread_pool.start(worker2)

                worker = Worker(finding_streams,options, url, main_window)
                thread_pool.start(worker)  # Submit the worker to the thread pool
                
                # Get the global QThreadPool instance
                worker.signals.streams_found.connect(lambda yt,streams,stream_audio,status: handle_streams_found(yt,streams,stream_audio,status,folder,window,main_window,thread_pool))

                window.close()

            else:
                window.close()

        except Exception as e:
            print("lamba error",e)
            error(e,main_window,thread_pool)
            window.close()

def finding_streams(options,url,main_window):

            yt =YouTube(url)
            stream_audio = 0
            status = None

            resolution = options.currentText()
            split_resolution = resolution.split("/")
            print("Youtube video title: ",yt.title)

            if split_resolution[0] == "highest":
                    streams = yt.streams.filter(progressive=True,file_extension="mp4").get_highest_resolution()
                    status = "proceed"
                
            elif split_resolution[0] == "mp3":
                    streams = yt.streams.filter(only_audio=True).first()
                    status = "audio"
                
            else:
                    streams = yt.streams.filter(res=f"{split_resolution[0]}",file_extension="mp4").first()

                    if 'progressive="True"' in str(streams):                                        
                        status = "proceed"
                        return yt,streams,stream_audio,status
                    else:
                        status = "join"
                        stream_audio = yt.streams.filter(only_audio=True).first()
                        return yt,streams,stream_audio,status
                
            return yt,streams,stream_audio,status
                

#Changing animations when the stream being found
def handle_streams_found(yt,streams,stream_audio,status,folder,window,main_window,thread_pool):

    print("Choosed stream:",streams)

    downloading_animation(main_window,thread_pool)

    if status == "audio":

        # Create an instance of Worker with download_video function and its arguments
        worker = Worker(download_audio,yt,streams,folder,main_window,thread_pool)
    
    elif status == "join":
         
        # Create an instance of Worker with download_video function and its arguments
        worker = Worker(join_video_and_download,yt,streams,stream_audio,folder,main_window,thread_pool)

    else:
        # Create an instance of Worker with download_video function and its arguments
        worker = Worker(download_video,streams,folder,main_window,thread_pool)

    thread_pool.start(worker)  # Submit the worker to the thread pool
    worker.signals.finished.connect(lambda: download_complete(main_window,thread_pool))


def join_video_and_download(yt,streams,stream_audio,folder,main_window,thread_pool):
     
    try: 
        print(stream_audio)

        title = re.sub(r'[|\\/?*]', '_', yt.title)

        path = (resource_path("resources"))
        audio_path = (resource_path("resources\ audio"))
        video = streams.download(output_path=path)
        if video:
            audio = stream_audio.download(output_path=audio_path) 
            if audio:     
                print("Audio: ",audio)
                print("Video: ",video)
                if "/" in folder:
                    back_slash = "/"
                    output_name = f"{folder+back_slash+title}.mp4"
                else:
                    forward_slash = "\ "
                    output_name = f"{folder+forward_slash+title}.mp4"
                print(output_name)
                video_converter.video_joiner(video,audio,output_name) 
                shutil.rmtree(audio_path)
                os.remove(video)
    
    except Exception as e:
        print(e)
        error(e,main_window,thread_pool)
     

def download_audio(yt,audio,folder,main_window,thread_pool):

    try: 

        title = re.sub(r'[|\\/?*]', '_', yt.title)

        path = (resource_path("resources"))
        download = audio.download(output_path=path)
        print(download)
        
        if "/" in folder:
            back_slash = "/"
            output_name = f"{folder+back_slash+title}.mp3"
        else:
            forward_slash = "\ "
            output_name = f"{folder+forward_slash+title}.mp3"
        print(output_name)
        video_converter.convert_to_mp3(download,output_name) 
        os.remove(download)
    
    except Exception as e:
        error(e,main_window,thread_pool)


def download_video(streams,folder,main_window,thread_pool):
            try:
                print ("Starting download ....")
                streams.download(output_path=folder)
                print("Download completed")
                    
            except Exception as e:
                print(e)
                error(e,main_window,thread_pool)

def downloading_animation(main_window,thread_pool):
        
    main_window.progress_label.clear()

    # Start loading animation
    signal_emitter = WorkerSignals()
    signal_emitter.update_signal.connect(main_window.downloading_animation)
    
    worker = WorkerAnimation(signal_emitter)
    thread_pool.start(worker)

def download_complete(main_window,thread_pool):

    try:

        main_window.progress_label.clear()

        # Start loading animation
        signal_emitter = WorkerSignals()
        signal_emitter.update_signal.connect(main_window.download_complete)
        
        worker = WorkerAnimation(signal_emitter)
        thread_pool.start(worker)

        worker.signals.finished.connect(main_window.show_info_message)
    
    except Exception as e:
        print(e)
        error(e,main_window,thread_pool)

def error(e,main_window,thread_pool):

    error = Worker(main_window.show_error_message,e)
    thread_pool.start(error)

class GUI(QMainWindow):
    def __init__(self):
        super(GUI,self).__init__()

        #Making a frameless window
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)

        #Loading GUI
        uic.loadUi( resource_path("design\main_window.ui"),self)
        self.setFixedSize(1089,729)

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
                    self.second_window = loadUi(resource_path("design\second_window.ui"))

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
            widget = self.childAt(event.pos())
            if widget is self.title_bar:
                self.draggable = True
                self.offset = event.pos() - self.pos()
            else:
                self.draggable = False

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
        
        self.loading_status = QtGui.QMovie(resource_path("resources\loading.gif"))
        self.progress_label.setMovie(self.loading_status)

        # Align the movie to the center of the QLabel
        self.progress_label.setAlignment(QtCore.Qt.AlignCenter)

        self.loading_status.start()
        if self.loading_status.isValid():
            print("loading animation working sucessfully")
        else:
            print("loading animation didn't load suceessfully")
    
    def downloading_animation(self):
        
        self.download_status = QtGui.QMovie(resource_path("resources\download_start.gif"))
        self.progress_label.setMovie(self.download_status)
        self.download_status.start()
        if self.download_status.isValid():
            print("downloading animation working sucessfully")
        else:
            print("downloading animation didn't load suceessfully")

    def download_complete(self):
        self.complete_status = QtGui.QMovie(resource_path("resources\download_complete.gif"))
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

