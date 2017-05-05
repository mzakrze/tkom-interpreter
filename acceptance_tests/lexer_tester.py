import os,sys,inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from lexer import *
from tokens import *
import glob, os

def get_line_generator_from_file(filename):
    fh = open(filename, 'r')
    for line in iter(fh):
		yield line
    fh.close()

folders = [file for file in glob.glob("*") if file[-3:] != ".py"]
for num, folder in enumerate(folders):
	try:
		print("\ntest nr " + str(num + 1) + ": " + str(folder))
		lexer = Lexer(get_line_generator_from_file(str(folder) + "/in"))
		tokens = []
		while True:
			tokens.append(lexer.calc_single_token())
			if tokens[-1] is None:
				tokens.pop()
				break
		with open((str(folder) + "/lexer_out")) as f:
			desired_output = f.read()
		lexer_out = ''
		for token in tokens :
			lexer_out += str(token) + '\n'
		if lexer_out == desired_output:
			print("    OK")
		else:
			filename = str(folder) + "/lexer_out_fail"
			with open(filename,"w") as out_file:
				out_file.write(lexer_out)
			print("    FAILED: output differs from desired")
			print("    output written in: " + filename)
	except IOError:
		print("   FAILED: files not found")