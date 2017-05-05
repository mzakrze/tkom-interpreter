from lexer import *
from tokens import *
from parser import *
import sys
import traceback

def main(filename):
	try:
		with open(filename) as openFile:
			lexer = Lexer(openFile.read()) # TODO: lexer refactor - take a generator of lines, or something
			output_stream = sys.stdout
			parser = Parser(lexer, output_stream)
			parser.execute_main()
	except LexerException as le:
		print(le.msg)
	except ParserException as pe:
		print(pe.msg)

if __name__ == "__main__":
	if len(sys.argv) < 1:
		print("Invalid use. Specify input file")
		# TODO - rozsadny komunikat jesli taki plik nie istnieje
		sys.exit()
	main(sys.argv[1])