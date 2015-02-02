def uniqueStrings(fileName):
	''' Pulls out data from file and returns a unique set of data
		For example. IF you have a list of things ['dog', 'dog', 'cat']
		It will return ['dog', 'cat']'''
	cache = []

	with open(fileName, 'r+') as f:
		for line in f:
			line = line.replace('\n', '')
			if line != '':
				cache.append(line)
				
	cache = list(set(cache))

	with open(fileName, 'w+') as f:
		for item in cache:
			f.write(item + '\n')

def main():
	uniqueStrings('commentIDcache.txt')

if __name__ == '__main__':
	main()
