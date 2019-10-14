"""Usage:
  wppAnalysis.py run <textfile> [--freqAnalysis=<freqAnalysis>] [--stopwords=<stopWords>] [--Iramuteq=<Iramuteq>]
"""
from docopt import docopt
from util import load_stop_words, load_Iramuteq
import abc,re,sys, csv

class AbstractClass(metaclass=abc.ABCMeta):

	def execution_steps(self, conversationPath):
		self.conversation_body_of_text = self._load_input(conversationPath)
		self.conversation_body_of_text = self._clean_data(self.conversation_body_of_text)
		self.conversation_body_of_text = self._remove_stop_words(self.conversation_body_of_text)
		self.conversation_body_of_text = self._apply_Iramuteq(self.conversation_body_of_text)
		self.freq_analysis = self._freq_analysis(self.conversation_body_of_text)
		self._save_freq_to_csv(self.freq_analysis)
		return self.freq_analysis

	@abc.abstractmethod
	def _load_input(conversationPath):
		pass

	@abc.abstractmethod
	def _clean_data(conversationPath):
		pass

	@abc.abstractmethod
	def _remove_stop_words(conversationBodyOfText):
		pass

	@abc.abstractmethod
	def _apply_Iramuteq(conversationBodyOfText):
		pass

	@abc.abstractmethod
	def _freq_analysis(conversationBodyOfText):
		pass 

class WhatsappConversationAnalysis(AbstractClass):

	def _load_input(self, conversationPath):
		return open(conversationPath, 'r').read()

	def _clean_data(self, conversation):
		regex_info_message = r"\[.*?\].{3,4}\d{2}.\d{2}.\d{4,5}.\d{4}.:*"
		lines = conversation.splitlines()
		result = ""
		for line in lines:
			line = line.strip()
			if line:
				result += re.sub(regex_info_message, "", line.lower()) + "\n"
		return result

	def _remove_stop_words(self, conversation):
		stop_words = load_stop_words()
		result = ""
		for word in conversation.split():
			if word not in stop_words:
				result += word + " "
		return result

	def _apply_Iramuteq(self, conversation):
		if not conversation: 
			return "please input a body of text in order to apply the Iramuteq filter"
			sys.exit(0)
		iramuteq_map = load_Iramuteq("word-equivalent")
		new_body_text = ""
		for word in conversation.split():
			if word in iramuteq_map:
				previous_value_of_word = word 
				word = iramuteq_map[word]
			new_body_text += word + " "
		return new_body_text	

	def _freq_analysis(self, conversation):
		if not conversation:
			return "please input a body of text in order to run the frequency analysis"
			sys.exit(0)
		freq_map = dict()
		for word in conversation.split():
			if word in freq_map:
				freq_map[word] += 1
			else:
				freq_map[word] = 1
		return freq_map

	def _save_freq_to_csv(self, freqDict):
		sorted_freqDict = sorted(freqDict.items(), key=lambda kv: -kv[1])
		with open('freq.csv', 'w') as csv_file:
			writer = csv.writer(csv_file)
			for key, value in sorted_freqDict:
				writer.writerow([key, value])


def Init(arguments):
	Wpp = WhatsappConversationAnalysis()
	Wpp.execution_steps(arguments['<textfile>'])

if __name__ == '__main__':
    arguments = docopt(__doc__, version='0.1.1rc')
    if arguments['<textfile>']:
    	Init(arguments)
    else: 
    	print("You should input a textfile")
