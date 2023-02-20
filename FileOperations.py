import os

DEFAULT_MODIFIERS_DIRECTORY = "Modifiers"

def findFileWithinDirectory(name, directory):
    files = os.listdir(directory)
    for file in files:
        path_full = directory + "/" + file
        if os.path.isdir(path_full):
            found = findFileWithinDirectory(name, path_full)
            if found is not None:
                return found
        elif os.path.isfile(path_full):
            if name == file:
                return path_full

    return None

def FindModifier(modifierName):
    return findFileWithinDirectory(modifierName, DEFAULT_MODIFIERS_DIRECTORY)