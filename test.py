try:
    from PIL import ImageTk,Image
except ImportError:
    import Image
import pytesseract

import argparse
import os


import Tkinter as tk

def foo():
	i = Image.open('Desk_reciepts/Image-00005.png')
	s = i.size
	#i.show()

	#if(s[0] < s[1]):
	#	i = i.transpose(Image.ROTATE_270)

	i.show()


	print(pytesseract.image_to_string(i,config='load_system_dawg = False, load_freq_dawg = False, --psm = 1'))

class GUI:
    def __init__(self, master, all_reciepts):
        self.master = master #get the master tkinter window.

        self.reciepts = all_reciepts

        self.master.title = "Doug's Reciept GUI" 
        tk.Label(master, text="Red X to stop", font='bold').grid(row=0,column=0)

        next = tk.Button(master,text="Show next image",command=self.show_next_image)
        next.grid(row=1,column=0)

        prev = tk.Button(master,text="Show previous image",command=self.show_previous_image)
        prev.grid(row=2,column=0)

        prev = tk.Button(master,text="Rotate Image Right",command=self.rotate_image_right)
        prev.grid(row=3,column=0)

        prev = tk.Button(master,text="Rotate Image Left",command=self.rotate_image_left)
        prev.grid(row=4,column=0)

        prev = tk.Button(master,text="RUN OCR",command=self.run_OCR)
        prev.grid(row=5,column=0)

        self.canvas = tk.Canvas(master,width=1000,height=1000)
        self.canvas.grid(row=10,column=3)

        self.imagetk_showing = None  #important quirk, have to save the reference to the image that is being shown so it doesn't get garbage collected
        self.image_showing = None #so I can remeber the image that I'm currently showing, so I can transform it
        self.num_showing_image = -1 #i'm not yet showing an image



    def show_next_image(self):
        self.show_image_number(self.num_showing_image + 1)


    def show_previous_image(self):
        self.show_image_number(self.num_showing_image - 1)

    def rotate_image_right(self):
        self.rotate_image(ROTATE_270)

    def rotate_image_left(self):
        self.rotate_image(IMAGE.ROTATE_90)
    
    def rotate_image(rotation):
        i = self.image_showing
        i = i.transpose(rotation)
        i_thumb = i.copy()
        i_thumb.thumbnail((1000, 1000), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(i_thumb)
        self.canvas.create_image(0,0,anchor=tk.NW,image=img)
        self.image_showing = i
        self.imagetk_showing = img

    def show_image_number(self,num):
        if (num < 0) or (num > len(self.reciepts) -1 ):
            return

        self.num_showing_image = num

        i = Image.open(self.reciepts[self.num_showing_image])
        #i.show()
        i_thumb = i.copy()
        i_thumb.thumbnail((1000, 1000), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(i_thumb)
        self.canvas.create_image(0,0,anchor=tk.NW,image=img)
        self.image_showing = i
        self.imagetk_showing = img


    def run_OCR(self):
        print(pytesseract.image_to_string(self.image_showing,config='load_system_dawg = False, load_freq_dawg = False'))




if __name__ == "__main__":
    print("Welcome to Doug's hyper-intelligent reciept parser.!")
    """ Creating the argparse """
    parser = argparse.ArgumentParser(description = 'Needs to know where to look for the reciepts.')
    parser.add_argument('folder', type = str, help = 'Needs to know where to look for the reciepts.' )
    parsed = parser.parse_args()

    #print(parsed)


    #crawl the folder that I'm told to look at, and generate a list of all my .png images.
    all_reciepts = []
    for root,dirs,files in os.walk(parsed.folder):
        for f in files:
            if ".png" in f:
                all_reciepts.append(os.path.join(root,f))
    print(all_reciepts)



    #great.  Now, I need to iterate through each one of these, show their images


    root = tk.Tk()
    my_gui = GUI(root,all_reciepts) #have to pass the controllers into the GUI so the callback factory can work.
    root.mainloop()