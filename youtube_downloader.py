from pytube import YouTube #NOTE: This module should be downloaded if not already
import customtkinter #NOTE: This module should be downloaded if not already

customtkinter.set_appearance_mode("default")
customtkinter.set_default_color_theme("blue")

class GUI(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        #Creating basic GUI codes
        self.title("Youtube video downloader")
        self.geometry("600x500")


        self.mainloop()
    
    def main_widgets(self):

        self.download_btn = customtkinter.CTkButton(self,text="Download video")

if __name__ =="__main__":
    GUI()
