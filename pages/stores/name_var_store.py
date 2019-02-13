try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

class NameVarStore(object):
	def __init__(self, controller, name, default_value=False):
		self.name = name
		self.holder = None
		self.controller = controller
		self.assignVariable(default_value)

	def assignVariable(self, default_value):
		if type(default_value) == type(True):
			holder = BooleanVar(self.controller)
			holder.set(default_value)
		elif type(default_value) == type('string'):
			holder = StringVar(self.controller)
			holder.set(default_value)
		else:
			holder = Variable(self.controller)
			holder.set(default_value)
		self.holder = holder

	def get(self):
		return self.holder.get()

	def set(self, value):
		self.holder.set(value)

	def __str__(self):
		return '%s is set to %s'%(self.name, self.get())

	def __repr__(self):
		return self.__str__()
