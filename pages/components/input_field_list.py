try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

import os
import tkFileDialog

class InputFieldList(object):
	def __init__(self, parent, controller, title, input_array, row, column, columnspan=1):
		self.input_array = input_array
		self.controller = controller
		self.parent = parent
		self.bulk_text = []

		lf_options = LabelFrame(parent, text=title, padx=15, font='Helvetica 14 bold')
		lf_options.grid(row=row+1, column=column, columnspan=columnspan, sticky='WENS', padx=5, pady=5, ipadx=5, ipady=5)
		lf_options.grid_rowconfigure(0, weight=1)
		lf_options.grid_columnconfigure(0, weight=1)

		row = 0

		lb_select_all = Label(lf_options, text='Select Number of inputs', font='Helvetica 13 bold')
		lb_select_all.grid(row=row, column=0, sticky="W", pady=3)

		options_count_list = tuple(list(range(14)))
		self.option_count = StringVar(parent)
		self.option_count.set(options_count_list[0])

		drop_down = apply(OptionMenu, (lf_options, self.option_count) + options_count_list)
		drop_down.grid(row=row, column=1, sticky='W', pady=3)
		self.option_count.trace('w', self.changeInDropDown)

		row += 1

		self.canvas = Canvas(lf_options)
		self.canvas.grid(row=row, column=0, columnspan=2, sticky='nwes')

		vsbar = Scrollbar(lf_options, orient="vertical", command=self.canvas.yview)
		vsbar.grid(row=row, column=2, sticky='ns')
		self.canvas.configure(yscrollcommand=vsbar.set)
		# self.canvas.bind_all("<MouseWheel>", self.mouseWheel)

		row += 1

		self.frame_inputs = Frame(self.canvas, relief=GROOVE)
		self.frame_inputs.grid(row=0, column=0, sticky='nwes')
		self.canvas_frame = self.canvas.create_window((0,0), window=self.frame_inputs, anchor='nw')
		self.canvas.bind('<Configure>', self.frameWidth)
		self.frame_inputs.bind("<Configure>", self.resize)

		lb_text_area = Label(lf_options, text='Or paste paths(one per line) in text area give below', font='Helvetica 13 bold')
		lb_text_area.grid(row=row, column=0, sticky="W", pady=3)

		self.sv_bulk_input = StringVar()
		self.sv_bulk_input.trace("w", lambda: self.bulkInputUpdate())
		self.text_area = Text(lf_options, height=15, bd=1, bg='gray86')
		self.text_area.grid(row=row+1, column=0, columnspan=3, sticky='nwes', padx=(0, 30))

		self.text_area.bind('<KeyRelease>', self.bulkInputUpdate)

		self.changeInDropDown()

	# def mouseWheel(self, event):
	# 	self.canvas.yview_scroll(-1*(event.delta/120), "units")

	def bulkInputUpdate(self, *args):
		text = self.text_area.get("1.0",END)
		text = text.strip().replace('\\n','\n').split('\n')
		self.bulk_text = [line.strip() for line in text if len(line.strip()) > 0]
		if len(self.bulk_text) > 0:
			self.changeInDropDown()

	def changeInDropDown(self, *args):
		for widget in self.frame_inputs.winfo_children():
			widget.destroy()

		while len(self.input_array) > 0:
			self.input_array.pop()

  		row = 0
		for index in range(max(len(self.controller.user_rois), int(self.option_count.get())) + len(self.bulk_text)):

			lb_path = Label(self.frame_inputs, text='Input #%d'%(index+1))
			lb_path.grid(row=row, column=0, sticky="W", pady=3)

			sv_path = StringVar()
			if index < len(self.controller.user_rois):
				sv_path.set(self.controller.user_rois[index].get())

			temp_index = max(len(self.controller.user_rois), int(self.option_count.get()))
			if index >= temp_index:
				sv_path.set(self.bulk_text[index - temp_index])


			en_path = Entry(self.frame_inputs, textvariable=sv_path, width = 50)
			en_path.grid(row=row, column=1, sticky="W", pady=3)

			btn_select = Button(self.frame_inputs, text='Select', command=lambda place_holder=sv_path: self.chooseDir(self.parent, self.controller, place_holder, 'input directory'))
			btn_select.grid(row=row, column=2, sticky='E', padx=5, pady=3)
			self.input_array.append(sv_path)
			row += 1

	def chooseDir(self, parent, controller, place_holder, message):
		current_dir = os.getcwd()
		parent.update()
		chosen_dir =  tkFileDialog.askopenfilename(parent=parent, initialdir = current_dir, title='Select the location of ' + message)
		place_holder.set(chosen_dir)

	def frameWidth(self, event):
		canvas_width = event.width
		self.canvas.itemconfig(self.canvas_frame, width = canvas_width)

	def resize(self, event):
		self.canvas.configure(scrollregion=self.canvas.bbox("all"), width=600, height=190)


