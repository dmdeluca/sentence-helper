import pickle, sys, os, time
import msvcrt

class word_predictor:

	# class initialization, creates a new dictionary
	def __init__(self):
		self.words = dict()

	# convenient function to add a new word object to the dictionary
	def add_word(self,LITERAL):
		self.words[LITERAL] = word(LITERAL)
		return self.words[LITERAL]

	# function that takes a string as an argument, removes all punctuation, and then returns the split string as a list of individual literals.
	def stll(self,STRING):
		#turn a string into a literals list
		new_string = STRING.replace('.','',1000)
		split_string = new_string.split(' ')
		return split_string

	# this function takes a user-generated string literal and either (a) adds it to the dictionary if it's not already in there, or (b) increases the word's likelihood of following the previous word.
	def read_text(self,STRING):
		literals_list = self.stll(STRING)
		for i in range(0,len(literals_list)):
			lit = literals_list[i]
			if lit not in self.words:
				self.add_word(lit)
			if i > 0:
				this_word = self.words[lit]
				prev_word = self.words[literals_list[i-1]]
				prev_word.increment_likelihood(this_word)
				prev_word.sort_nexts()

	#load the dictionary object from an external file, or create a new dictionary if there is no existing file.
	def load_word_bank(self):
		try:
			with open("wordbank.sav",'rb') as file:
				self.words = pickle.load(file)
		except:
			print("File not found. Creating first file.")
			self.words = dict()

	# save the dictionary object to a file.
	def save_word_bank(self):
		try:
			with open("wordbank.sav",'wb') as file:
				pickle.dump(self.words,file,pickle.HIGHEST_PROTOCOL)
		except:
			print("There was a problem saving the file")
			return -1
		else:
			print("Word bank saved.")
			return 1

	# print all the words in the dictionary, along with their likely followers.
	def print_dictionary(self):
		for key,word_object in self.words.items():
			print(key)
			for each_word in word_object.nexts:
				primary_literal = each_word[0].literal
				print("   >"+primary_literal)
				for c,each_subword in enumerate(each_word[0].nexts,1):
					secondary_literal = each_subword[0].literal
					print("     >"+secondary_literal)
					if c > 2:
						break

class word:
	
	def __init__(self,LITERAL):
		self.literal = LITERAL
		# nexts is a list of duples, each of which contains a word object and an integer which represents the number of times it has appeared after this word
		self.nexts = []
	
		
	def sort_nexts(self):
		self.nexts.sort(key = lambda x:x[1],reverse = True)


	def get_most_likely(self,n):
		self.sort_nexts()
		return_list = [self.nexts[i][0].literal for i in range(0,min(n,len(self.nexts)))]
		return return_list

	#self-explanatory?
	def find_duple_containing_word(self,FINDWORD):
		for c,each_duple in enumerate(self.nexts,0):
			if self.nexts[c][0] == FINDWORD:
				return c
		return -1

	def increment_likelihood(self,WORD):
		#THISWORD and NEXTWORD are both word objects
		#this function serves to either: add the NEXTWORD with count 1 (as duple) to THISWORD's list of NEXTs, or increase the count of the NEXTWORD duple in THISWORD's list of nexts
		index = self.find_duple_containing_word(WORD)
		if index != -1:
			#increase likelihood
			self.nexts[index][1] += 1
		else:
			#add the duple with word NEXTWORD and count 1
			self.nexts.append([WORD,1])

def main_loop():

	#fire up the word predictor object
	predictor = word_predictor()
	predictor.load_word_bank()
	
	#plus some other vars
	user_input = ''
	str_accum = ""
	counter = 0

	#some basic ascii variables
	first_valid_character = 32
	last_valid_character = 126
	zero_character = 48
	nine_character = 57

	#begin a loop
	while True:
		
		print_it = 0
		
		x = msvcrt.getch()

		# if the key pressed corresponds to an acceptable word character, then we'll take it in and look at it. If it's not a number, we'll just add it to the working string. If it is a number, though, we will use it to choose the next word in the input string.
		if ord(x) >= first_valid_character and ord(x) <= last_valid_character:
			if ord(x) >= zero_character and ord(x) <= nine_character:
				if ord(x)-zero_character >= len(possible_next_words):
					str_accum += predictor.words[possible_next_words[ord(x)-zero_character]]
			else:
				str_accum += chr(ord(x))
		elif ord(x) == 13:
			predictor.read_text(str_accum)
			os.system("cls")
			print("Read new text and updated dictionary.")
			time.sleep(1)
			os.system("cls")
			#do a little eye-candy thing where the previous sentence disappears one character at a time.
			while len(str_accum) > 0:
				print(str_accum+" "*100,end='\r')
				str_accum = str_accum[:-1]
				time.sleep(0.01)
			os.system("cls")
		elif ord(x) == 27:
			break

		#we have to do manual backspaces because we're updating the console in real time. I think...?
		if ord(x) == 8:
			str_accum = str_accum[:-1]

		#generate a list of word suggestions based on the last word in the typed sentence.
		possible_next_words = []
		if str_accum != "":
			split_word_list = str_accum.strip().split(' ')
			last_word = split_word_list[len(split_word_list)-1]
			if last_word in predictor.words:
				if len(predictor.words[last_word].nexts)>0:
					possible_next_words = [predictor.words[last_word].nexts[i][0] for i in range(0,len(predictor.words[last_word].nexts))]
					print_it = 1

		#clear the screen.
		os.system("cls")

		#get the length of the base string we've been accumulating.
		base = str_accum+"_ --> "
		base_len = len(base)-1

		#now, if there is a list of words we need to print, we print it as a little list on the right hand side of the sentence.
		if print_it:
			print(str_accum+"_ --> 1. "+possible_next_words[0].literal+" *")
			for i in range(1,len(possible_next_words)-1):
				print(" "*base_len+str(i+1)+". "+possible_next_words[i].literal)
		
		#and here is the default print suffix.
		else:
			print(str_accum+"_ --> ?",end='\r')

	# clear the screen.
	os.system("cls")

	predictor.save_word_bank()

main_loop()
