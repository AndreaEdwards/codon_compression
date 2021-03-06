from time import time

# this is a codon usage dictionary that is generated by the current program.
# in this case, the user has selected to remove the amino acid C and only wants 
# the codons with ranking of 3 or higher (i.e. the first three codons with 
# the highest usage)
dictionary = {'A': [{'GCC': '0.45'}, {'GCT': '0.19'}, {'GCG': '0.19'}], 'E': [{'GAG': '0.67'}, {'GAA': '0.33'}], 'D': [{'GAT': '0.53'}, {'GAC': '0.47'}], 'G': [{'GGC': '0.43'}, {'GGA': '0.29'}, {'GGT': '0.21'}], 'F': [{'TTC': '0.63'}, {'TTT': '0.37'}], 'I': [{'ATC': '0.47'}, {'ATT': '0.34'}, {'ATA': '0.19'}], 'H': [{'CAC': '0.6'}, {'CAT': '0.4'}], 'K': [{'AAG': '0.71'}, {'AAA': '0.29'}], 'M': [{'ATG': '1'}], 'L': [{'CTG': '0.43'}, {'TTG': '0.18'}, {'CTC': '0.15'}], 'N': [{'AAC': '0.56'}, {'AAT': '0.44'}], 'Q': [{'CAG': '0.7'}, {'CAA': '0.3'}], 'P': [{'CCC': '0.33'}, {'CCG': '0.29'}, {'CCA': '0.25'}], 'S': [{'AGC': '0.25'}, {'TCC': '0.24'}, {'TCG': '0.2'}], 'R': [{'CGC': '0.33'}, {'CGT': '0.16'}, {'CGA': '0.15'}], 'T': [{'ACC': '0.38'}, {'ACG': '0.26'}, {'ACA': '0.19'}], 'W': [{'TGG': '1'}], 'V': [{'GTG': '0.47'}, {'GTC': '0.24'}, {'GTT': '0.18'}], 'Y': [{'TAC': '0.63'}, {'TAT': '0.37'}], 'X': [{'TAA': '0.42'}, {'TAG': '0.32'}, {'TGA': '0.26'}]}

# your job is to write a script that finds every possible combination of these 
# codons. the information we are really interested in is the length of the
# compressed codon list (we want the shortest list) and the sum of the 
# codon usage frequencies of codons in the compressed list

# below is the function that I need help on. "DoWork". 
# currently, it does not work correctly
# it is sampling some combinations more than once, and skipping other combinations

def DoWork(codon_count, idx, processes, empty_list, new_dict, redundancy, rules_dict, tot_combinations, GlobalStart):
	"""
	Parameters
	----------
	idx : int
		probably short for index. this is the process number we are on
	"""
	print("Thread " + str(processes) + " starting")
	BestReduceSize = 20
	BestRatio = 0
	BestIndex = 0
	StartTime = time()
	t = 0
	stop = 0
	
	while stop == 0:
		for i in range(len(empty_list)):
			for j in range(0, i + 1): 
				if (empty_list[j] + 1) % codon_count[j] != 0:
					if t % processes == idx:
						codons, ratios = CreateListFromIndex(empty_list, new_dict)
						if redundancy != 0:
							pass
						else:
							recursive = Recursive(codons, rules_dict)
							reduced_list = recursive.Reduce()
							total_usage_frequency = 0
							for frequency in ratios:
								total_usage_frequency += float(frequency)
							if len(reduced_list) < BestReduceSize or (len(reduced_list) == BestReduceSize and total_usage_frequency > BestRatio):
								BestList = [codons, ratios]
								BestReduceSize = len(reduced_list)
								BestIndex = t 
								BestRatio = total_usage_frequency
								BestZ = empty_list
					#print report every 1000 iter
					if t % 10000 == 0:
						EndTime = time()
						print("thread " + str(processes) + 
								" finished " + 
								str(int(100 * t/tot_combinations)) + 
								" % @ " + 
								str(int((time()- GlobalStart) * 1000)) +
								" ms Best Size: " +
								str(BestReduceSize) +
								", Best Index: " +
								str(BestIndex) +
								", Best Ratio: " +
								str(BestRatio))
						StartTime = EndTime
					#advance the index
					empty_list[j] += 1
					t += 1
					
				else:
					empty_list[j] = 0
					t += 1
	
				if i == len(empty_list):
					stop = 1		

	information_dict = {
	"BestList" : BestList,
	"ReduceSize" : BestReduceSize,
	"Ratio" : BestRatio
	}
	return information_dict


# these are the functions that DoWork relies on
def CreateListFromIndex(empty_list, new_dict):
	codons = []
	ratios = []
	i = 0
	while i < len(empty_list):
		for key1 in new_dict:
			for key2 in new_dict[key1][empty_list[i]]:
				codons.append(key2)
				ratios.append(new_dict[key1][empty_list[i]][key2])
			i += 1
	return codons, ratios

class Recursive:
	def __init__(self, codon_list, rules_dict):
		"""Initialize the Recursive object with two parameters.

		Parameters
		----------
		codon_list: list
			list of codons that are most frequently used after removing codons 
			corresponding to amino acids (or stop codon) that the user has 
			specified they want left out. This list can be the result of 
			running BestList
		rules_dict: dict
			dictionary in which the key is a string resulting from joining the 
			nucleotides (A, G, C, T) in columns 2-5 of each line from the .rul
			file and the value corresponds to the string in the first column of
			each line of the .rul file

		Returns
		-------
		none
		
		Examples
		--------
		>>> recursive = Recursive(best_list, rules_dict)
		"""			
		self.codon_list = codon_list
		self.rules_dict = rules_dict
		self.reduced = []
		self.my_dict = {}

	def FindMinList(self, list):
		"""Recursive algorithm in which the self.codon_list is a list of the
		most frequently used codons for amino acids that the user wants to 
		include for compression. self.codon is initially the list passed in
		when instantiating the Recursive class. This list is copied to the
		variable temp for downstream comparison. Then, Reduce() is called and
		the resulting list is captured in the variable reduced_list. The two
		lists are compared and if not equal, FindMinList recurses by calling
		itself and passing the new list (captured from Reduce()) in as the
		argument. When temp and reduced_list are equal, the method returns the
		updated self.codon_list (this member variable is modified in Reduce())

		Parameters
		----------
		list: list
			This is a codon list, it can correspond to any codon list such as
			the most frequently used codons staged for compression or the 
			semi-compressed list resulting from Reduce()

		Returns
		-------
		self.codon_list: list
			The updated codon list. This list represents the most compressed 
			set of codons remaining after running the recursive algorithm once
			through. (need better description of this)

		Examples
		--------
		>>> recursive = Recursive(best_list, rules_dict)
		>>> recursive.FindMinList(best_list)
		"""

		temp = self.codon_list
		reduced_list = self.Reduce()
		if temp != reduced_list:
			self.FindMinList(reduced_list)
		return self.codon_list

	def Reduce(self):
		"""Iterate through each position in the codon. At each position,
		capture the result of Grouping(int) in self.my_dict. Pass this dict to
		ListFromGroup(dict, int) and capture the result in self.codon_list. Return
		self.codon_list after iterating through each position in the codon.
		
		Parameters
		----------
		none

		Returns
		-------
		self.codon_list: list
			The updated codon list. This list represents the most compressed 
			set of codons remaining after running Grouping(int) and 
			ListFromGroup(dict, int) for all three codon positions

		Examples
		--------
		reduced_list = self.Reduce()

		"""
		for i in range(3):
			self.my_dict = self.Grouping(i)
			self.codon_list = self.ListFromGroup(self.my_dict, i)
		return self.codon_list

	def Grouping(self, int):
		"""This function initializes an empty dict. Then iterates through each
		codon in self.codon_list. The code then branches depending on which 
		codon position was passed in (0, 1, or 2). If int == 0, InRules == 0 
		and the codon is split into two variables ('position' == the first 
		position and 'remainder' == the rest of the codon). Then it iterates 
		through the keys in self.rules_dict and checks if the value is equal to
		the position. If so, then it adds a new key-value pair to the local 
		my_dict variable. The key corresponds to the "remainder" and the value 
		is a set that contains the split key from self.rules_dict and the 
		InRules variable is set to 1. If the value in self.rules_dict is not
		equivalent to the position, then nothing happens. After exiting the
		if branch, the script checks whether InRules is 1 or 0. If 0, then
		my_dict is extended. If a key already exists in this dict with the 
		same value as the remainder, then the value of that key is (which is 
		a set) is extended to include the new value of the position variable.
		If not, then a new key-value pair is added. The logic is the same for 
		int == 1 and int == 2. The script then iterates through the keys in 
		my_dict and joins the value's strings.

		Parameters
		----------
		int : int
			This should be a 0, 1, or 2 (depending on what is being passed
			from Reduce()). Because we are interested in positions in the
			codons, it does not make sense to have numbers other than 0, 1, 
			or 2. There should be error handling here.

		Returns
		-------
		self.my_dict : dict 
			A dictionary in which the keys are strings of nucleotides that fall
			at particular positions in the codon (1,2 or 0,2 or 0,1) and the 
			values are all the nucleotides that can exist at the remaining 
			position. Here the key-value pairs represent compressed codons. 
	
			For example, the first iteration through looks like:
			{'AA': 'AGT', 'AC': 'A', 'GT': 'C', 'AG': 'C', 'CC': 'A', 
			'TT': 'AT', 'CG': 'CG', 'GG': 'T', 'GC': 'AG', 'AT': 'CGT', 
			'TG': 'ACG'}

			And the last iteration through looks like:
			{'BA': 'T', 'CG': 'T', 'CA': 'G', 'AM': 'C', 'DA': 'A', 
			'RG': 'C', 'WT': 'T', 'VT': 'G', 'SC': 'G', 'TG': 'G'}

		Examples
		--------
		>>> self.my_dict = self.Grouping(i)
		"""
		my_dict = {}
		for codon in self.codon_list:
			if int == 0:
				position = codon[int]
				remainder = codon[int+1:]
				InRules = 0
				for key in self.rules_dict:
					if self.rules_dict[key] == position:
						if remainder in my_dict:
							my_dict[remainder].add(key.split())
						else:
							my_dict[remainder] = set(key.split())
						InRules = 1
			elif int == 1:
				position = codon[int]
				remainder = codon[0] + codon[2]
				InRules = 0
				for key in self.rules_dict:
					if self.rules_dict[key] == position:
						if remainder in my_dict:
							my_dict[remainder].add(key.split())
						else:
							my_dict[remainder] = set(key.split())
						InRules = 1
			else:
				position = codon[int]
				remainder = codon[:2]
				InRules = 0
				for key in self.rules_dict:
					if self.rules_dict[key] == position:
						if remainder in my_dict:
							my_dict[remainder].add(key.split())
						else:
							my_dict[remainder] = set(key.split())
						InRules = 1
			if InRules == 0:
				if remainder in my_dict:
					my_dict[remainder].add(position)
				else:
					my_dict[remainder] = set(position)
		for key in my_dict:
			my_dict[key] = ''.join(sorted(my_dict[key]))
		self.my_dict = my_dict
		return self.my_dict

	def ListFromGroup(self, my_dict, int):
		"""This function initializes an empty list. Then iterates through the
		keys in the member variable self.my_dict (which was modified in 
		Grouping(int)) and captures the value in the variable temp. The code
		then branches depending on what integer was passed in (0, 1, or 2).
		If 0, it checks whether the value (a string) is longer than 1. If it
		is, then it finds the value from the member variable self.rules_dict 
		and concatenates it with the key from self.my_dict. The concatenated
		product is then captured in the variable 'new_codon'. If it is not
		longer than one (i.e. only one nucleotide will work at that particular
		position in the compressed codon), then the value at self.my_dict[key]
		is concatenated with the key from self.my_dict and this concatenated
		product is captured in the variable 'new_codon'. new_codon is then
		added to the new_list. Logic is similar for int values of 1 or 2. 

		Parameters
		----------
		my_dict : dict
			This dictionary has a string as the key and string as value. The
			dictionary should be the same format as the output from Grouping()
		int : int
			This should be a 0, 1, or 2. Because we are interested in positions
			in the codons, it does not make sense to have numbers other than 
			0, 1, or 2. There should be error handling here.
		
		Returns
		-------
		new_list : list
			A list of compressed codons

		Examples
		--------
		>>> self.codon_list = self.ListFromGroup(self.my_dict, i)
		"""
		new_list = []
		for key in self.my_dict:
			temp = self.my_dict[key]
			if int == 0:
				if len(self.my_dict[key]) > 1:
					new_codon = self.rules_dict[temp] + key
					new_list.append(new_codon)
				else:
					new_codon = self.my_dict[key] + key
					new_list.append(new_codon)
			elif int == 1:
				if len(self.my_dict[key]) > 1:
					nt = self.my_dict[key]
					new_codon = key[0] + self.rules_dict[temp] + key[1]
					new_list.append(new_codon)
				else:
					nt = self.my_dict[key]
					new_codon = key[0] + self.my_dict[key] + key[1]
					new_list.append(new_codon)
			else:
				if len(self.my_dict[key]) > 1:
					new_codon =  key + self.rules_dict[temp]
					new_list.append(new_codon)
				else:
					new_codon = key + self.my_dict[key]
					new_list.append(new_codon)
		return new_list

def main():
	codon_count = [3, 2, 2, 3, 2, 3, 2, 2, 1, 3, 2, 2, 3, 3, 3, 3, 1, 3, 2, 3]
	idx = 0
	processes = 1
	empty_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# same as the dictionary above.. this is the most important piece of information. if you can figure out how to get at the answer without all the other garbage.. that would be awesome.
	new_dict = {'A': [{'GCG': '0.33'}, {'GCC': '0.26'}, {'GCA': '0.23'}], 'E': [{'GAA': '0.68'}, {'GAG': '0.32'}], 'D': [{'GAT': '0.63'}, {'GAC': '0.37'}], 'G': [{'GGC': '0.37'}, {'GGT': '0.35'}, {'GGG': '0.15'}], 'F': [{'TTT': '0.58'}, {'TTC': '0.42'}], 'I': [{'ATT': '0.49'}, {'ATC': '0.39'}, {'ATA': '0.11'}], 'H': [{'CAT': '0.57'}, {'CAC': '0.43'}], 'K': [{'AAA': '0.74'}, {'AAG': '0.26'}], 'M': [{'ATG': '1'}], 'L': [{'CTG': '0.47'}, {'TTA': '0.14'}, {'TTG': '0.13'}], 'N': [{'AAC': '0.51'}, {'AAT': '0.49'}], 'Q': [{'CAG': '0.66'}, {'CAA': '0.34'}], 'P': [{'CCG': '0.49'}, {'CCA': '0.2'}, {'CCT': '0.18'}], 'S': [{'AGC': '0.25'}, {'TCT': '0.17'}, {'AGT': '0.16'}], 'R': [{'CGT': '0.36'}, {'CGC': '0.36'}, {'CGG': '0.11'}], 'T': [{'ACC': '0.4'}, {'ACG': '0.25'}, {'ACT': '0.19'}], 'W': [{'TGG': '1'}], 'V': [{'GTG': '0.35'}, {'GTT': '0.28'}, {'GTC': '0.2'}], 'Y': [{'TAT': '0.59'}, {'TAC': '0.41'}], 'X': [{'TAA': '0.61'}, {'TGA': '0.3'}, {'TAG': '0.09'}]}
	redundancy = 0
	rules_dict = {'AC': 'M', 'GT': 'K', 'ACG': 'V', 'ACGT': 'N', 'AG': 'R', 'CG': 'S', 'AT': 'W', 'ACT': 'H', 'AGT': 'D', 'CGT': 'B', 'CT': 'Y'}
	tot_combinations = 15116544
	GlobalStart = time()
	DoWork(codon_count, idx, processes, empty_list, new_dict, redundancy, rules_dict, tot_combinations, GlobalStart)

main()
























