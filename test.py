try:
    from PIL import ImageTk,Image
except ImportError:
    import Image
import pytesseract

import argparse
import os
import shutil

import datetime


import date_entry


import Tkinter as tk
from tkinter import ttk

import all_suppliers

def foo():
    i = Image.open('Desk_reciepts/Image-00005.png')
    s = i.size
    #i.show()

    #if(s[0] < s[1]):
    #   i = i.transpose(Image.ROTATE_270)

    i.show()


    print(pytesseract.image_to_string(i,config='load_system_dawg = False, load_freq_dawg = False, --psm = 1'))

class GUI:

    def __init__(self, master, all_reciept_paths, original_dir, output_dir, processed_dir):
        self.master = master #get the master tkinter window.

        self.master.title("Doug's Reciept GUI")
        tk.Label(master, text="Red X to stop", font='bold').grid(row=0,column=0)

        ttk.Separator(master, orient=tk.HORIZONTAL).grid(row = 1, column=0, columnspan=1, sticky=(tk.E,tk.W))

        self.reciept_controls = tk.Frame(master).grid(row=2,column=0)

        tk.Label(master,text="Reciept Controls",font='bold').grid(row=2,column=0)

        next = tk.Button(master,text="Show next image",command=self.show_next_image)
        next.grid(row=3,column=0)

        prev = tk.Button(master,text="Show previous image",command=self.show_previous_image)
        prev.grid(row=4,column=0)

        prev = tk.Button(master,text="Rotate Image Right",command=self.rotate_image_right)
        prev.grid(row=5,column=0)

        prev = tk.Button(master,text="Rotate Image Left",command=self.rotate_image_left)
        prev.grid(row=6,column=0)

        prev = tk.Button(master,text="RUN OCR",command=self.run_OCR)
        prev.grid(row=7,column=0)

        self.canvas = tk.Canvas(master,width=1000,height=1000)
        self.canvas.grid(row=1,column=3,rowspan=200,columnspan=10) #set rowspan to impossibly large number, to hack the spacing in Row=0 to look normal

        tk.Label(root,text="Day / Month / Year").grid(row=8,column=0)

        self.date = date_entry.DateEntry(root)
        self.date.grid(row=9,column=0)

        process_date = tk.Button(master,text="Process Date",command=self.read_date)
        process_date.grid(row=10,column=0)

        tk.Label(root,text="Supplier").grid(row=11,column=0)

        self.supplier_choice = tk.StringVar(master)
        supplier = tk.OptionMenu(master,self.supplier_choice,*all_suppliers.suppliers) #point it to the all_suppliers for options for now.  TODO: New supplier.
        supplier.grid(row=12,column=0)

        tk.Label(root,text="Explanation").grid(row=13,column=0)
        self.explanation = tk.StringVar()
        explanation_entry = tk.Entry(root,textvariable = self.explanation).grid(row=14,column=0)

        tk.Label(root,text="Price").grid(row=15,column=0)
        self.price = tk.StringVar()
        price_entry = tk.Entry(root,textvariable = self.price).grid(row=16,column=0)

        process_fields = tk.Button(master,text="Process Reciept",command=self.process_reciept).grid(row=17,column=0)


        #a variable, which updates if the reciept that is showing has or has not been processed.  Must be updated every time 'process' or 'show new image' is called.
        self.this_reciept_processed = tk.BooleanVar()
        self.this_reciept_processed.set(False)

        #a variable, which shows the name that has been assigned to this reciept (if any)
        self.new_name = tk.StringVar()
        self.new_name.set("None")


        tk.Label(root,text="Processed Status: ").grid(row=0,column=1)
        self.is_processed = tk.Label(root,textvariable = self.this_reciept_processed).grid(row=0,column=2)

        tk.Label(root,text="Processed Name: ").grid(row=0,column=3)
        self.new_name_disp = tk.Label(root,textvariable = self.new_name).grid(row=0,column=4)



        self.reciepts = all_reciept_paths #an array, len(all_reciepts) long, containing the path to the original reciepts.  We can't actually move them untill the end, otherwise the show_image_number will break
        self.processed = [False]*len(all_reciepts) #an array, showing if the reciept has been processed or not.
        self.new_path = [None]*len(all_reciepts) #an array, showing the new path for the reciept.  Need to know this in case we need to overwrite it.


        #original dir is the directory these files come from.  Output is where renamed copies go.  processed is where the ones that are renamed go (keeping their original name)
        self.original_dir = original_dir
        self.output_dir = output_dir
        self.processed_dir = processed_dir

        self.imagetk_showing = None  #important quirk, have to save the reference to the image that is being shown so it doesn't get garbage collected
        self.image_showing = None #so I can remeber the image that I'm currently showing, so I can transform it
        self.num_showing_image = -1 #i'm not yet showing an image




    def show_next_image(self):
        self.show_image_number(self.num_showing_image + 1)


    def show_previous_image(self):
        self.show_image_number(self.num_showing_image - 1)

    def rotate_image_right(self):
        self.rotate_image(Image.ROTATE_270)

    def rotate_image_left(self):
        self.rotate_image(Image.ROTATE_90)
    
    def rotate_image(self,rotation):
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

        self.this_reciept_processed.set(self.processed[self.num_showing_image])
        self.new_name.set(self.new_path[self.num_showing_image])

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

    def read_date(self):
        date_arr = self.date.get()
        return date_arr[2] + "-" + date_arr[1] + "-" + date_arr[0]


    def process_reciept(self):
        if self.new_path[self.num_showing_image] is not None:
            #that means i've processed it before, but I want to rename it.  That means the old filename has to go.
            os.remove(os.path.join(self.output_dir,self.new_path[self.num_showing_image]))

        #come up with the new name
        new_name = "[" + self.read_date() + "]" + " " + str(self.supplier_choice.get()) + " " + str(self.explanation.get()) + " $" + str(self.price.get()) + ".png"


        #set things up
        self.this_reciept_processed.set(True)
        self.processed[self.num_showing_image] = True  #when I close down, all the files listed as "processed" will get moved

        self.new_path[self.num_showing_image] = new_name
        self.new_name.set(new_name)

        head = os.path.split(self.reciepts[self.num_showing_image])[0] #this contains the foldernames of the path, without the filename itself, but WITH the foldername and /originals.
        head = head.replace(self.original_dir,'') #get rid of the filename itself and the /originals
        head = head[1:] #getrid of the leading /

        #ok.  I have a new name, and I know the old name.  Time to do some copy-pastaing.
        shutil.copyfile(self.reciepts[self.num_showing_image],os.path.join(self.output_dir,head,new_name))





if __name__ == "__main__":
    print("Welcome to Doug's hyper-intelligent reciept parser.!")
    """ Creating the argparse """
    parser = argparse.ArgumentParser(description = 'Needs to know where to look for the reciepts.')
    parser.add_argument('input_folder', type = str, help = 'Needs to know where to look for the reciepts.' )

    #parser.add_argument('renamed_folder',type = str, nargs='?',default="./renamed", help="Folder with renamed reciepts.  Creates if it doesn't exist.  Defaults to ./output")
    #parser.add_argument('processed_folder',type = str, nargs='?',default="./processed", help="Folder with all processed reciepts.  Creates if it doesn't exist.  Defaults to ./output")


    parsed = parser.parse_args()


    #first, let's create my working directory, so I don't break someone's folder
    working_directory = str(datetime.datetime.now()).replace(" ","_").replace(":","_")
    os.mkdir(working_directory)

    #subdirectories
    originals = os.path.join(working_directory,'originals')
    os.mkdir(originals)
    output = os.path.join(working_directory,'renamed_output')
    os.mkdir(output)
    processed = os.path.join(working_directory,'processed')
    os.mkdir(processed)

    #crawl the input folder, copy over files into new_dir/originals
    all_reciepts = []
    for root,dirs,files in os.walk(parsed.input_folder):
        for f in files:
            if ".png" in f:
                #step 1.  Make sure originals, rename_output, and processed have identical filestructures
                #can get away with checking only the originals,root b/c all three directories were just made
                if not os.path.exists(os.path.join(originals,root)):
                    os.mkdir(os.path.join(originals,root))
                    os.mkdir(os.path.join(output,root))                    
                    os.mkdir(os.path.join(processed,root))

                #step 2, copy the file
                shutil.copyfile(os.path.join(root,f),os.path.join(originals,root,f))


    #ok, now that I created the folders, that means in the future that I can copy any file name from my originals, into output or processed, and it won't break.                  

    #crawl the folder that I'm told to look at, and generate a list of all my .png images.
    all_reciepts = []
    for root,dirs,files in os.walk(originals):
        for f in files:
            if ".png" in f:
                all_reciepts.append(os.path.join(root,f))
    

    #great!  I now have a list of all my filenames, and the original/output/processed directories that I can copy/paste into.


    root = tk.Tk()
    my_gui = GUI(root,all_reciepts,originals,output,processed) #have to pass the controllers into the GUI so the callback factory can work.
    root.mainloop()