try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

from .base_input import *


class RegistrationInputPage(BaseInputPage, object):
	def __init__(self, parent, controller, frame_number):
		BaseInputPage.__init__(self, parent, controller, frame_number)

		lf_reg = tk.LabelFrame(self, text='Configuration for FLIRT', font='Helvetica 14 bold', padx=15)
		lf_reg.grid(row=self.starting_row+1, column=0, columnspan=3, sticky='nsew', ipadx=10, ipady=10)
		lf_reg.grid_rowconfigure(0, weight=1)
		lf_reg.grid_columnconfigure(3, weight=1)

		lb_cost_func = LabelToolTip(lf_reg, text="1. Cost Function", tool_tip_text=self.controller.desc.reg_ext_cost_func)
		lb_cost_func.grid(row=0, column=0, sticky="W", pady=3)

		en_cost_func = Entry(lf_reg, textvariable=controller.sv_reg_cost_func, width = 46)
		en_cost_func.grid(row=0, column=1, sticky="W", pady=3)

		lb_reg_ref = LabelToolTip(lf_reg, text="2. Reference", tool_tip_text=self.controller.desc.reg_ext_reference)
		lb_reg_ref.grid(row=1, column=0, sticky="W", pady=3)

		en_reg_ref = Entry(lf_reg, textvariable=controller.sv_reg_reference, width = 46)
		en_reg_ref.grid(row=1, column=1, sticky="W", pady=3)

		button_ref_ref = tk.Button(lf_reg, text='Browse', command=lambda : self.chooseFile(self, controller, controller.sv_reg_reference, 'Registration Reference'))
		button_ref_ref.grid(row=1, column=2, sticky='W', padx=5, pady=3)

		wrapper = Frame(lf_reg)
		wrapper.grid(row=3, column=0, sticky="WE", columnspan=3, pady=(3, 20))
		wrapper.grid_rowconfigure(0, weight=1)
		wrapper.grid_columnconfigure(2, weight=1)

	def onShowFrame(self, event):
		super(RegistrationInputPage, self).onShowFrame(event)
		if not self.controller.b_registration.get():
			super(RegistrationInputPage, self).moveToNextPage(is_parent=False)
		elif not (self.controller.sv_registration_method.get().strip().lower() == 'flirt'):
			super(RegistrationInputPage, self).moveToNextPage(is_parent=False)
		else:
			self.silentMode()


	def setFrameTitle(self):
		self.title.set('Registration')

	def moveToNextPage(self):
		if self.controller.b_registration.get() and (self.controller.sv_registration_method.get().strip().lower() == 'flirt') \
			and (not self.controller.sv_reg_cost_func.get().strip() \
			or not self.isValidPath(self.controller.sv_reg_reference.get().strip())):
			self.setRequiredInputError('Provide valid inputs for FLIRT')
			return
		super(RegistrationInputPage, self).moveToNextPage()

