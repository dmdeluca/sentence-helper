import pickle, sys, os, time, msvcrt, winsound, math, random

class word_predictor:

	# class initialization, creates a new dictionary
	def __init__(self):
		self.words = dict()

	# convenient function to add a new word object to the dictionary
	def add_word(self,LITERAL):
		self.words[LITERAL] = word(LITERAL)
		return self.words[LITERAL]

	#create new entries in the dictionary for very common pairings
	def consolidate(self):
		#check all entries in the dictionary to see if there are very common pairings
		for word_literal, word_object in self.words.items():
			for each_possible_next_word in word_object.nexts:
				if each_possible_next_word[1] > 10:
					new_word = add_word(word_literal+" "+each_possible_next_word[0].literal)
					word_object.increment_likelihood(new_word,10)

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
			
			#first we'll check for individual word matches
			lit = literals_list[i]
			if lit not in self.words:
				self.add_word(lit)
			if i > 0:
				this_word = self.words[lit]
				prev_word = self.words[literals_list[i-1]]
				prev_word.increment_likelihood(this_word)

				#now we're going to check for matches of word pairs.
				#this code fits here logically because we would only ever check for this if we were past the first word and had a "previous word" in the sequence to refer to.
				if i < len(literals_list)-1:

					#store the pair
					lit_pair = literals_list[i]+" "+literals_list[i+1]
					if lit_pair not in self.words:
						#add the word pair to the dictionary if it doesn't already exist
						self.add_word(lit_pair)

					#since we've gotten here (in the logic), it means there is a word pair in the dictionary, so we can reference it
					this_word_pair = self.words[lit_pair]
					prev_word.increment_likelihood(this_word_pair)

				#sort all the previous word's followers based on likelihood
				prev_word.sort_nexts()

		#consolidate the dictionary
		self.consolidate()

	#load the dictionary object from an external file, or create a new dictionary if there is no existing file.
	def load_word_bank(self):
		try:
			with open("wordbank.sav",'rb') as file:
				self.words = pickle.load(file)
				return 1
		except:
			print("File not found. Creating first file.")
			self.words = dict()
			return 0

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
	
	#sort the words in word list according to their frequency number
	def sort_nexts(self):
		self.nexts.sort(key = lambda x:x[1],reverse = True)

	#return the most likely words to follow a word
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

	#increase the likelihood of a certain word occurring after this word
	def increment_likelihood(self,WORD,value=1):
		index = self.find_duple_containing_word(WORD)
		if index != -1:
			self.nexts[index][1] += value
		else:
			self.nexts.append([WORD,value])

#show a message that says, "Press any key to continue."
def any_key_message():
	nothing = input("\nPress any key to continue. ")

#Print messages slowly.
def slow_message(STRING):
	print(STRING)
	time.sleep(1.5)

#self-explanatory
def happy_sound():
	play_tones([0,4,7,12],[150],2)
	time.sleep(.5)

#display an ironic loading bar with optional musical interlude
def fake_loading_bar(gradient=50,loading_message="LOADING",loaded_message="LOADING COMPLETE",invert=0,load_tones=[0,4,7,9,14]):
	
	if invert:
		load_tones.reverse()

	for i in range(0,gradient):

		winsound.Beep(int(2**math.floor(i/gradient*10/(len(load_tones)-1))*220*2**(load_tones[int((i+i/gradient)%(len(load_tones)))]/12)),100)

		print("LOADING: "+"#"*int((i+1)/gradient*20)+">"+"-"*int((gradient-i-1)/gradient*20),end='\r')

		time.sleep(.5/gradient)

	print("\n"+loaded_message)

	happy_sound()

def play_tones(tone_list,duration_list=[100],octave=1):
	
	#this function takes a list of tones and a list of durations and produces a series of windows beeps to match.
	tl = tone_list
	dl = duration_list
	
	#this makes the two lists equal in length.
	while len(tl) > len(dl):
		dl.append(dl[0])
	while len(dl) > len(tl):
		dl.append(0)
	
	#both lists should be equal now
	for i in range(len(tl)):
		winsound.Beep(int(octave*220*2**(tl[i%(len(tl))]/12)),dl[i])
		winsound.SND_ASYNC

#remove all the punctuation from a string
def clean(STRING):
	punctuation_marks = ['.',',',"!","?"]
	clean_string = STRING
	for p in punctuation_marks:
		clean_string.replace(p,"")
	return clean_string

def main_loop():

	#welcome message
	slow_message("Hi, and welcome to this little word suggester app. Let me check to see if we have been working on a library together.")

	any_key_message()

	fake_loading_bar(35,"Searching for our past conversations...","\nSearch complete!"+" "*100,0,[0,7,12,16])

	#fire up the word predictor object
	predictor = word_predictor()
	load_success = predictor.load_word_bank()

	if load_success:
		slow_message("\nLooks like we have been talking for a while already. Let's just keep the conversation going.")
	else:
		slow_message("\nLooks like we've never spoken before in our lives. Let's fix that! I made a new save file just for us. <3")

	any_key_message()

	slow_message("\nLet's get to know each other a bit. All you need to do is type sentences to me in the console. I'll read whatever you write, and then sometimes I'll try to finish your sentences like a true robot companion would.")

	slow_message("\nAll this will disappear when you press enter.")

	any_key_message()

	os.system("cls")

	#get some other vars ready
	user_input = ''
	str_accum = ""
	counter = 0
	possible_next_words = []
	max_words = 8
	partials = 0

	#some basic ascii variables
	first_valid_character = 32
	last_valid_character = 126
	zero_character = 48
	nine_character = 57

	#begin a loop
	while True:
		
		#reset this every key_press
		print_it = 0
		
		#store the keypress value
		x = msvcrt.getch()

		# if the key pressed corresponds to an acceptable word character, then we'll take it in and look at it. If it's not a number, we'll just add it to the working string. If it is a number, though, we will use it to choose the next word in the input string.

		key = ord(x)

		#check to see whether the key pressed was an acceptable word character
		if key >= first_valid_character and key <= last_valid_character:

			#check to see if it's a number
			if key >= zero_character and key <= nine_character:

				#check to see if it's one of the numbers listed
				if key-zero_character >= 0 and key-zero_character < 10 and possible_next_words != [] and key-zero_character <= len(possible_next_words):

					#and if all these conditions are met, add the chosen word to the built string
					if partials == 1:
						str_accum = str_accum.strip() + predictor.words[possible_next_words[key-zero_character-1].literal].literal[len(last_word):]
					else:
						str_accum = str_accum.strip() +" "+ predictor.words[possible_next_words[key-zero_character-1].literal].literal
			else:

				#else, just add a character like normal
				str_accum += chr(key)

		#special condition: the user has pressed ENTER!
		elif key == 13:

			#ingest the typed string and alter the dictionary accordingly.
			predictor.read_text(str_accum)

			#clear the screen to make way for the next message
			os.system("cls")
			slow_message("Read new text and updated dictionary.")

			#clear that screen again
			os.system("cls")

			#do a little eye-candy thing where the previous sentence disappears one character at a time.
			chr_sq = ['\\','|','/','-']
			word_sq = ['','*MUNCH*',' *MUNCH*','','','']
			while len(str_accum) > 0:
				os.system("cls")
				print(str_accum+chr_sq[len(str_accum) % 4]+word_sq[len(str_accum) % 5]+" "*100,end='\r')
				str_accum = str_accum[:-int(math.ceil(len(str_accum)/50))]
				time.sleep(0.01)
			os.system("cls")
			str_accum = ""

		#special condition: escape key is pressed. this means we're done.
		elif key == 27:
			break

		#we have to do manual backspaces because we're updating the console in real time. I think...?
		if ord(x) == 8:
			str_accum = str_accum[:-1]

		# generate a list of word suggestions based on the last word in the typed sentence.
		# update 4-23-18: display a maximum of 8 words.
		possible_next_words = []
		if str_accum != "":
			#split up the typed string into an indexable list
			split_word_list = clean(str_accum).strip().split(' ')
			#store the last word in the cleaned string, for clean code
			last_word = split_word_list[len(split_word_list)-1]
			#store the second-to-last word because we'll need it for auto-complete later...but only if there are at least two words in the split string. Otherwise we get an out-of-range error.
			if len(split_word_list)-2 > 0:
				second_to_last_word = split_word_list[len(split_word_list)-2]
			#self-explanatory...now we are checking to see if last_word is one of our recognized words
			if last_word in predictor.words:
				#store the list of next possible words to make code cleaner-looking
				nx = predictor.words[last_word].nexts
				#only display next possible words if there is actually a typed string
				if len(nx)>0:
					#display up to a maximum number of words
					possible_next_words = [nx[i][0] for i in range(0,min(len(nx),max_words+1))]
					print_it = 1
					partials = 0
			#so, it's clear that "last word" is either not a recognized word or is just not a complete word
			else:
				#is it the beginning of any word in the dictionary?
				possible_next_words = []
				for word_literal, word_object in predictor.words.items():
					#if the word-partial is in one of our dictionary words, list that dictionary word
					#limit the number of results to max_words
					if word_literal.find(last_word) != -1 and len(possible_next_words) < max_words:
						#add the word to the list of possible words
						possible_next_words.append(word_object)
						print_it = 1
						partials = 1

		#clear the screen.
		os.system("cls")

		#get the length of the base string we've been accumulating.
		base = str_accum+"_ --> "
		base_len = len(base)

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

	#save the word bank.
	predictor.save_word_bank()

#run the program
main_loop()
