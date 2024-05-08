from tkinter import filedialog,messagebox

from pytube import YouTube #NOTE: This module should be downloaded if not already
import customtkinter #NOTE: This module should be downloaded if not already
import pyperclip #NOTE: This module should be downloaded if not already

customtkinter.set_appearance_mode("default")
customtkinter.set_default_color_theme("blue")

#Function to paste the copied url
def url_paste(widget):
    copied_url = pyperclip.paste()
    widget.insert(0,copied_url)
    

class GUI(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        #Creating basic GUI codes
        self.title("Youtube video downloader")
        self.geometry("700x500")

        self.main = self.main_widgets()


        self.mainloop()
    
    def main_widgets(self):

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

        self.entry.grid(row=0,column=0,sticky = "nw", padx=(50,0),pady=(150,0))
        self.paste_btn.grid(row=0,column=0,sticky = "nw",padx=(370,0),pady=(150,0))
        self.download_btn.grid(row=0,column=0,sticky = "nw",padx=(530,0),pady=(150,0))
    
    def download_window(self):

        #create download window
        self.up= customtkinter.CTkToplevel(self.master)
        self.up.title("Download")
        self.up.geometry("300x200")
        
        
        self.label = customtkinter.CTkLabel(self.up,text="Select you're resolution:")
        self.label.focus()

        resolutions = ["360p","480p","720p","highest"]
        self.options = customtkinter.CTkComboBox(self.up,values=resolutions)

        self.download = customtkinter.CTkButton(self.up,text="Download",
                                                    fg_color="red",
                                                    hover_color="#cc0000",
                                                    font=("Helvetica",13),
                                                    width=20,
                                                    height=25,
                                                    corner_radius=40,
                                                    command=self.download_window_func)
        

        self.label.grid(row=0,column=0,sticky = "nw", padx=(20,0),pady=(50,0))
        self.options.grid(row=0,column=0,sticky = "nw", padx=(160,0),pady=(50,0))
        self.download.grid(row=0,column=0,sticky = "nw", padx=(200,0),pady=(150,0))
        
    
    def download_window_func(self):
        try:
            url = self.entry.get()
            folder = filedialog.askdirectory()
            yt =YouTube(url)
            resolution = self.options.get()

            if resolution == "highest":
                streams = yt.streams.filter(progressive=True,file_extension="mp4")
                highest_resolution_video = streams.get_highest_resolution()
                highest_resolution_video.download(output_path=folder)
                self.up.destroy()
            else:
                streams = yt.streams.filter(res=f"{resolution}",file_extension="mp4").first()
                streams.download(output_path=folder)
                self.up.destroy()


        except Exception as e:
            messagebox.showerror("Error",f"{e}")
            self.up.destroy()


if __name__ =="__main__":
    GUI()
