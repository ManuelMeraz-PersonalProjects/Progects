def cachedict(filename):
    '''
    Pulls information from file and creates a dictionary with
    a key and the rest of the line split into a list for the values.
    
    dicty = {key:[val1, val2, val3]}
    '''
    cache = {}
    try:
        with open(filename, 'r') as f:
            
            # separates the lines in file
            for item in f.read().splitlines():
                
                # Creates 2 variables with the key and value
                (key, value) = item.rstrip().split(None, 1)
                
                # Splits the value string into a list
                value = value.split(' ')
                
                cache[key] = value
            print ('Cache created')
            
    except ValueError:
        print ('Registry empty')
    
    return cache
        

def cachelist(filename):  
    '''
    Pulls information from file and creates a list with
    a key and the rest of the line split into a list for the values.
    '''          
    cache = set()
        
    with open(filename, 'r') as f:
        # drop trailing newlines
        cache_read = [line.rstrip() for line in f.readlines()]

        # add them to set (this also handles duplicate entries if they occur)
        [cache.add(comment) for comment in cache_read]

    return cache
    
def writefile(filename, cache):
    ''' Function to write cache data to a file'''

    print('Writing data to {0}'.format(filename))

    with open(filename, 'w+') as f:
        if type(cache) == dict:
            for key in cache:
                f.write(key + ' ',)
                for value in cache[key]:
                    f.write(str(value) + ' ')
                f.write('\n')
        else:
            for item in cache:                   
                f.write(item + '\n')

    print('The file {0} has been updated'.format(filename))

  

    
def main():
    pass
    


if __name__ == '__main__':
    main()
