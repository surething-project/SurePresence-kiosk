from threading import Thread

from card import readCard

def remove_spaces(string):
    """Remove spaces between hexadecimal characters of the characteristics' value"""
    final = []
    for i in range(len(string)):
        if (string[i]) != ' ':
            final.append(string[i])
    return ''.join(final)

