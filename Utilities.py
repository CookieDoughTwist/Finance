
def consolidate_dict_array(dict_array,keys=None):
    """ Condense an array of dictionaries into a dictionary of arrays """
    # Input keys allows the user to define which dictionary keys
    # to consolidate. Passing nothing will consolidate all keys.
    # This function assumes that every dictionary in array_dict
    # has the same keyset.    
    if keys is None:
        keys = dict_array[0].keys()      
    array_dict = dict()
    for key in keys:
        array_dict[key] = list()        
    for d in dict_array:
        for key in keys:
            array_dict[key].append(d[key])
    return array_dict
    

def main():
    print "test utilities"


if __name__ == "__main__":
    main()