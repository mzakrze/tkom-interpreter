from tokens import *

class Lexer:
	def __init__(self, programString):
		self.programString = programString
		self.charPointer = 0

	"""
		convention: currChar() points at first un-read sign
	"""
	def calc_single_token(self):
		self.ommitAnyCommentsAndWhiteSigns()
		if self.isPointerOutOfRange():
			return None
		""" convention: any of this function: 
				1) successes and returns not None and moves self.charPointer
				2) failes, returns None, and does not alter self.charPointer
		"""
		literalsToCheck = (self.checkAsNumericLiteral, self.checkAsStringLiteral, self.checkForRestLiterals) # TODO: check if check2charsToken necessary
		for function in literalsToCheck:
			token = function()
			if token is not None:
				return token
		return None

	def checkAsNumericLiteral(self):
		def is_digit():
		    try:
		        int(self.currChar())
		        return True
		    except ValueError:
		        return False
		is_positive = 1
		had_dot = False
		if not is_digit():
			if self.currChar() == "-": #check if literal is negative
				is_positive = -1
				self.incPointer()
				if not is_digit():
					self.decPointer()
					return None
			else:
				return None
		literal = []
		separators = (' ', '\n', ']','(', ')', ',', ':', ';','+','-','*','/','%')
		while True:
			if self.currChar() == '.':
				if had_dot:
					raise Exception # has dot second time
				else:
					had_dot = True
					literal.append('.')
					self.incPointer()
			elif is_digit():
				literal.append(self.currChar())
				self.incPointer()
			elif self.currChar() in separators: 
				if had_dot:
					return Token(TokenType.NUM_LITERAL_DOUBLE, is_positive * float(''.join(literal)), self.charPointer)
				else:
					return Token(TokenType.NUM_LITERAL_INT, is_positive * int(''.join(literal)), self.charPointer)
			elif self.currChar().isalpha():
				while True:
					if self.currChar() in separators:
						token = Token(TokenType.ILLEGAL_TOKEN, ''.join(literal), self.charPointer)
						raise Exception
						raise LexerException(token, "Cannot resolve symbol: ")
					else:
						literal.append(self.currChar())
						self.incPointer()
			else:
				raise Exception
	
	def checkAsStringLiteral(self):
		if self.currChar() != '"':
			return None
		literal = []
		self.incPointer() #swallow '"'
		while True:
			if self.currChar() == '"' and self.programString[self.charPointer - 1] != '\\': # check also if " was escaped inside quotation
				break
			literal.append(self.currChar())
			self.incPointer()
		self.incPointer() # swallow '"'
		return Token(TokenType.STRING_LITERAL, ''.join(literal), self.charPointer) 

	def checkForRestLiterals(self):
		separators = ('[',']', ':', ';', ' ', ',' ,'.', '(', ')','!', '+', '-', '*', '/', '%', '&', '|', '\n','{','}','<','>','=')
		offset = 0
		while self.charPointer + offset < len(self.programString):
			if self.programString[self.charPointer + offset] in separators:
				if offset == 0: # first character is a separator: possible tokens e.g. <=, ==, && or any 1 char token
					# first: try to get longest token
					token = TokenType.getMatchingElseNone(''.join(self.programString[self.charPointer:self.charPointer + 2])) 
					if token is not None:
						self.charPointer += 2
						return Token(token, token.value, self.charPointer)
					 # second: if that fails, try shorter token
					token = TokenType.getMatchingElseNone(''.join(self.programString[self.charPointer]))
					if token is not None:
						self.charPointer += 1
						return Token(token, token.value, self.charPointer)
					else:
						raise Exception # TODO - add some apropriate exception
				else: # token is identifier or mnemonic token(if,else,return), and cannot be token like <, ==, && etc\
					token = TokenType.getMatchingElseNone(''.join(self.programString[self.charPointer:self.charPointer + offset]))
					if token is not None:
						self.charPointer += offset
						return Token(token, token.value, self.charPointer)
					else:
						arg = self.charPointer
						self.charPointer += offset
						return Token(TokenType.IDENTIFIER, ''.join(self.programString[arg:arg + offset]), self.charPointer)
			else:
				offset += 1

	def ommitAnyCommentsAndWhiteSigns(self):
		"""
		both call themselves recursively, becaouse after comment can be white spaces and after white spaces can bo comm
		"""
		try:
			self.ommitAnyWhiteSigns()
			self.ommitAnyComments()
		except IndexError:
			return 

	def ommitAnyComments(self):
		if self.currChar() == '/':
			self.incPointer()
			if self.currChar() == '/':
				while self.currChar() != '\n':
					self.incPointer()
				self.ommitAnyWhiteSigns() 
			elif self.currChar() == '*':
				self.incPointer()
				while self.currChar() != '*' or self.incPointerAndGetCurrChar() != '/':
					self.incPointer()
				self.incPointer()
				self.ommitAnyWhiteSigns()
			else:
				self.decPointer()

	def ommitAnyWhiteSigns(self):
		if self.isPointerOutOfRange():
			return
		while self.currChar() in (' ', '\n', chr(9)): # chr(9) is ASCII code for tab
			self.incPointer()
		self.ommitAnyComments()

	def currChar(self):
		return self.programString[self.charPointer]

	def incPointer(self):
		self.charPointer = self.charPointer + 1

	def decPointer(self):
		self.charPointer = self.charPointer - 1

	def incPointerAndGetCurrChar(self):
		self.incPointer()
		return self.currChar()

	def isPointerOutOfRange(self):
		return self.charPointer > len(self.programString) - 1 or self.currChar() is None

class LexerException(Exception):
	def __init__(self, token, message, trace = None):
		self.token = token
		self.message = message
		self.trace = trace
	
	def getLog(self, programString):
		line_string, line_nr, offset = self.calculateLine(programString)
		log = "Error at line " + str(line_nr) + ":\n"
		log += line_string + "\n"
		log += '^'.rjust(offset) + "\n"
		log += self.message + self.token.value + "\n"
		print("log is <" + log + ">endlog")
		return log

	def calculateLine(self, programString):
		line_nr = 1
		line_starts_at = 0
		for i in range(0, self.token.pointer):
			if programString[i] == '\n':
				line_nr += 1
				line_starts_at = i + 1
		
		line_stops_at = line_starts_at
		while programString[line_stops_at] != '\n':
			line_stops_at += 1

		line_string = programString[line_starts_at : line_stops_at]
		offset = 0
		for i in range(0, len(line_string)):
			if i + line_starts_at < self.token.pointer:
				if str(line_string[i]) == chr(9):
					offset += 8
				else:
					offset += 1
		return (line_string, line_nr, offset)