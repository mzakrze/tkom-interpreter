import os,sys,inspect

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


folders = [file for file in glob.glob("*") if file[-3:] != ".py"]
for num, folder in enumerate(folders):
	try:
		print("\ntest nr " + str(num + 1) + ": " + str(folder))
		file = str(folder) + "/in"
		lexer = Lexer(get_line_generator_from_file(file))
		iostreamMock = IOStreamMock()
		parser = Parser(lexer, iostreamMock)
		parser.execute_main()
		parser_out = iostreamMock.bufor
		with open((str(folder) + "/parser_out")) as f:
			desired_output = f.read()
		if parser_out == desired_output:
			print("    OK")
		else:
			filename = str(folder) + "/parser_out_fail"
			with open(filename,"w") as out_file:
				out_file.write(parser_out)
			print("    FAILED: output differs from desired")
			print("    output written in: " + filename)
	except LexerException as le:
		print(le.msg)
	except ParserException as pe:
		print(pe.msg)
	except IOError:
		print("   FAILED: files not found")