import threading

class StoppableThread(threading.Thread):

	def __init__(self, target=None, args=()):
		super(StoppableThread, self).__init__(target=target, args=args)
		self._stop_event = threading.Event()

	# def run(self):
	# 	if sys.version_info[0] == 2:
	# 		self._Thread__target(*self._Thread__args, **self._Thread__kwargs)
	# 	else: # assuming v3
	# 		self._target(*self._args, **self._kwargs)

	def stop(self):
		self._stop_event.set()

	def stopped(self):
		return self._stop_event.is_set()