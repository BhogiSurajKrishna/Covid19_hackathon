import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

import numpy as np
import tflearn
import tensorflow
import random
import json
import pickle

with open("intents.json") as file:
	data = json.load(file)

# try:
# 	with open("data.pickle", "rb") as f:
# 	 	words, labels, training, output = pickle.load(f)
#except:
words = []
labels= []
docs_x= []
docs_y= []

for intent in data["intents"]:  #Loop on All question types
	for pattern in intent["patterns"]: #All patterns in a single question type,i.e; all the sentences
		wrds = nltk.word_tokenize(pattern) # divides based on space
		words.extend(wrds)
		docs_x.append(wrds) #docs_x contains all sentences as a list of words,i.e;list of lists of words
		docs_y.append(intent["tag"])

	if intent["tag"] not in labels:
		labels.append(intent["tag"])

words = [stemmer.stem(w.lower()) for w in words if w != "?"] #stemmer reduces similar words into a single word
words = sorted(list(set(words))) #set makes sure it doesn't have duplicates

labels = sorted(labels)

training = []
output   = []

out_empty = [0 for _ in range(len(labels))]

for x,doc in enumerate(docs_x):
	bag = []

	wrds = [stemmer.stem(w) for w in doc]

	for w in words:
		if w in wrds:
			bag.append(1)
		else:
			bag.append(0)

	output_row = out_empty[:]
	output_row[labels.index(docs_y[x])] = 1

	training.append(bag)
	output.append(output_row)


training = np.array((training))
output = np.array((output))

with open("data.pickle", "wb") as f:
	pickle.dump((words, labels, training, output), f) # = pickle.load(f)

tensorflow.reset_default_graph()

net = tflearn.input_data(shape=[None,len(training[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(output[0]), activation = "softmax")
net = tflearn.regression(net)

model = tflearn.DNN(net)

# try:
# 	model.load("model.tflearn")
# except:
model.fit(training, output, n_epoch=1000, batch_size=8, show_metric=True)
model.save("model.tflearn")


def bag_of_words(s, words):
	bag = [0 for _ in range(len(words))]

	s_words = nltk.word_tokenize(s)
	s_words = [stemmer.stem(word.lower()) for word in s_words]

	for se in s_words:
		for i,w in enumerate(words):
			if w == se:
				bag[i] = 1

	return np.array((bag))


def chat():
	print("Start talking with the bot (type quit to stop)!")
	while True:
		inp = input("You: ")
		if stemmer.stem(inp.lower()) == "quit":
			break

		results = model.predict([bag_of_words(inp, words)])[0]

		results1 = np.array(results)
		results1 = (results1 >= 0.4)
		valid =[]
		for y,r in enumerate(results1):
			if(r == 1):
				valid.append(labels[y])
		for i1 in data["intents"]:
			if i1["tag"] in valid:
				if "context_set" in i1:
					context[userid] = i1["context_set"]

				if not "context_filter" in i1 or (userid in context and "context_filter" in i1 and i1["context_filter"] == context[userid]):
					print(random.choice(i1["responses"])) 
					
		results_index = np.argmax(results)
		tag = labels[results_index]

		if results[results_index] > 0.7:
			for tg in data["intents"]:
				if tg["tag"] == tag:
					responses = tg["responses"]

			print(random.choice(responses))
		else:
			print("I didn't get that, try again.")

chat()
#print(docs)
#print(wrds)
#print(labels)