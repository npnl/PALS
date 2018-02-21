try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

import tkFileDialog
import os

LARGE_FONT = ("Verdana", 12)
 
class MainWindow(tk.Tk):
	def __init__(self, *args, **kwargs):
		tk.Tk.__init__(self, *args, **kwargs)
		self.title("SQRL")
		self.geometry("300x300")

		self.sv_input_dir = StringVar(self)
  		self.sv_input_dir.set('')
		self.sv_output_dir = StringVar(self)
  		self.sv_output_dir.set('')
 
		# this container contains all the pages
		container = tk.Frame(self)
		container.pack(side="top", fill="both", expand=True)
		self.frames = {}
 
		for PageType in (DirectoryInputPage, PageOne):
			frame = PageType(container, self)
			self.frames[PageType] = frame 
 
		self.show_frame(DirectoryInputPage)
 
	def show_frame(self, name):
		frame = self.frames[name]
		frame.tkraise()
 
class DirectoryInputPage(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)

		Label(parent, text="Input Dir").grid(row=0, sticky=W)
		Label(parent, text="Output Dir").grid(row=1, sticky=W)

		en_input_dir = Entry(parent, textvariable=controller.sv_input_dir)
		en_output_dir = Entry(parent, textvariable=controller.sv_output_dir)

		en_input_dir.grid(row=0, column=1)
		en_output_dir.grid(row=1, column=1)

		button1 = tk.Button(parent, text='Select', command=lambda : self.chooseDir(parent, controller, controller.sv_input_dir))

		button1.grid(row=0, column=2)

		button2 = tk.Button(parent, text='Select', command=lambda : self.chooseDir(parent, controller, controller.sv_output_dir))
		button2.grid(row=1, column=2)


	def chooseDir(self, parent, controller, place_holder):
		current_dir = os.getcwd()
		parent.update()
		chosen_dir =  tkFileDialog.askdirectory(parent=parent, initialdir = current_dir, title='Select the location of your input directory')
		place_holder.set(chosen_dir)

	def checkValues(self, controller):
		print controller.sv_input_dir.get()
		print controller.sv_output_dir.get()
 
class PageOne(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		label = tk.Label(self, text='Page One', font=LARGE_FONT)
		label.pack(pady=10, padx=10)
 
		button1 = tk.Button(self, text='Back to Home',
							command=lambda : controller.show_frame(DirectoryInputPage))
		button1.pack()
 
if __name__ == '__main__':
	app = MainWindow()
	app.mainloop()
