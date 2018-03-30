import os

def isValidPath(filePath):
    if os.path.exists(filePath):
        pass
    elif os.access(os.path.dirname(filePath), os.W_OK):
        pass
    else:
        return False
    return True