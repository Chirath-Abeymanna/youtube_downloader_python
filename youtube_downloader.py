from tkinter import filedialog,messagebox
import threading

from pytube import YouTube #NOTE: This module should be downloaded if not already
import customtkinter #NOTE: This module should be downloaded if not already
import pyperclip #NOTE: This module should be downloaded if not already

customtkinter.set_appearance_mode("default")
customtkinter.set_default_color_theme("blue")

#Function to paste the copied url
def url_paste(widget):
    copied_url = pyperclip.paste()
    widget.delete(0,customtkinter.END)
    widget.insert(0,copied_url)

def download_window_func(entry,options,window,progress_bar):

        try:
            
            folder = filedialog.askdirectory()
            download_thread  = threading.Thread(target=download_video,args=(entry,options,window,folder,progress_bar))
            download_thread.start()
            window.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"{e}")
            window.destroy()

def download_video(entry,options,window,folder,progress_bar):
         
        try:
            url = entry.get()
            yt =YouTube(url,on_progress_callback= progress_status)
            resolution = options
            try:

                if resolution == "highest":
                    streams = yt.streams.filter(progressive=True,file_extension="mp4")
                    highest_resolution_video = streams.get_highest_resolution()
                    highest_resolution_video.download(output_path=folder)
                    messagebox.showinfo("Status","Download completed")
                    window.destroy()
                else:
                    streams = yt.streams.filter(res=f"{resolution}",file_extension="mp4").first()
                    streams.download(output_path=folder)
                    messagebox.showinfo("Status","Download completed")
                    window.destroy()
            
            except Exception as e:
                messagebox.showerror("Error",f"{e}")
                window.destroy() 

        except Exception as e:
            messagebox.showerror("Error",f"{e}")
            window.destroy()

class GUI(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        #Creating basic GUI codes
        self.title("Youtube video downloader")
        self.geometry("700x500")

        self.main = self.main_widgets()


        self.mainloop()
    
    def main_widgets(self):

        #global progress_bar

        self.download_btn = customtkinter.CTkButton(self,text="Download video",
                                                    fg_color="red",
                                                    hover_color="#cc0000",
                                                    font=("Helvetica",16),
                                                    width=40,
                                                    height=50,
                                                    corner_radius=40,
                                                    command=self.download_window)
        
        self.paste_btn = customtkinter.CTkButton(self,text="Paste the URL",
                                                    font=("Helvetica",16),
                                                    width=40,
                                                    height=50,
                                                    corner_radius=40,
                                                    command=lambda: url_paste(self.entry))
        
        self.entry = customtkinter.CTkEntry(self,placeholder_text="Paste you're URL here",font=("Helvetica",20),width=300,height=50)

        #self.progress = customtkinter.CTkProgressBar(self,height=20,width=300)
        #progress_bar = self.progress 

        self.entry.grid(row=0,column=0,sticky = "nw", padx=(50,0),pady=(150,0))
        self.paste_btn.grid(row=0,column=0,sticky = "nw",padx=(370,0),pady=(150,0))
        self.download_btn.grid(row=0,column=0,sticky = "nw",padx=(530,0),pady=(150,0))
        #self.progress.grid(row=0,column=0,sticky = "nw",padx=(150,0),pady=(250,0))
    
    def download_window(self):

        if self.entry.get() != "":

            #create download window
            self.up= customtkinter.CTkToplevel(self.master)
            self.up.title("Download")
            self.up.geometry("300x200")
            
            
            self.label = customtkinter.CTkLabel(self.up,text="Select you're resolution:")
            self.label.focus()

            resolutions = ["360p","480p","720p","highest"]
            self.options = customtkinter.CTkComboBox(self.up,values=resolutions)

            options = self.options.get()

            self.download = customtkinter.CTkButton(self.up,text="Download",
                                                        fg_color="red",
                                                        hover_color="#cc0000",
                                                        font=("Helvetica",13),
                                                        width=20,
                                                        height=25,
                                                        corner_radius=40,
                                                        command=lambda: download_window_func(self.entry,options,self.up,self.progress))
            

            self.label.grid(row=0,column=0,sticky = "nw", padx=(20,0),pady=(50,0))
            self.options.grid(row=0,column=0,sticky = "nw", padx=(160,0),pady=(50,0))
            self.download.grid(row=0,column=0,sticky = "nw", padx=(200,0),pady=(150,0))
        
        else:
            messagebox.showwarning("URL Not found","No URL was given")
       
def progress_status(stream,chunk,bytes_remaining):

    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    progress = int(bytes_downloaded / total_size * 100)
    progress_bar["value"] = progress


if __name__ =="__main__":
    GUI()
