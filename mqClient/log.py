def log(data):
    with open('log.txt', 'a') as fw:
        fw.write(data + '\n')
