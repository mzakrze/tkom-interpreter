import os,sys,inspect
import traceback
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from lexer import *
from tokens import *
from parser import *
import glob, os


class IOStreamMock:
    def __init__(self):
        self.bufor = ""
    def write(self, text):
		self.bufor += text

def get_line_generator_from_file(filename):
    fh = open(filename)
    for line in iter(fh):
		yield line
    fh.close()


files = [file for file in glob.glob("*") if file[-3:] != ".py" and file[-4:] != "_out"]

for file in files:
    try:
        filename = str(file)
        lexer = Lexer(get_line_generator_from_file(filename))
        iostreamMock = IOStreamMock()
        parser = Parser(lexer, iostreamMock)
        parser.execute_main()
        out_file = open(str(file) + "_out","w")
    except IOError:
		print("   FAILED: files not found")
    except LexerException as le:
        iostreamMock.write(le.msg)
    except ParserException as pe:
        iostreamMock.write(pe.msg)
    except Exception:
        iostreamMock.write(traceback.format_exc())
    finally:
        with open(str(file) + "_out", "w") as out_file:
            out_file.write(iostreamMock.bufor)


