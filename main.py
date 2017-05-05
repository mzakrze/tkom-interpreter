from lexer import *
from tokens import *
from parser import *
import sys
import traceback


def get_line_generator_from_file(filename):
    fh = open(filename, 'r')
    for line in iter(fh):
		yield line
    fh.close()

def main(filename):
	try:
		with open(filename) as openFile:
			lexer = Lexer(get_line_generator_from_file(filename))
			output_stream = sys.stdout
			parser = Parser(lexer, output_stream)
			parser.execute_main()
	except LexerException as le:
		print(le.msg)
	except ParserException as pe:
		print(pe.msg)

if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("Invalid use. Specify input file")
		# TODO - rozsadny komunikat jesli taki plik nie istnieje
		sys.exit()
	main(sys.argv[1])