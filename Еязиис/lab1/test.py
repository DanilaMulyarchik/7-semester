with open('paths.txt', 'r') as f:
    files = [i.strip() for i in f.readlines()]

documents = {}
for i in files:
    with open(i, 'r') as f:
        data = f.readlines()
    documents[i] = data[0]
print(documents)