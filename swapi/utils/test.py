import time

import petl

def change_delimiter(from_file, to_fiel):
    table = petl.fromcsv(from_file)
    petl.appendcsv(table, to_fiel, delimiter=":", write_header=True)

def second():
    for i in range(10):
        time.sleep(1)
        yield "person"

def first():
    print('hwllo')
    yield from second()
    print('world')
if __name__ == '__main__':
    # change_delimiter('big_file_delimiter.csv','big_file_delimiter.csv')
    # change_delimiter('small_file_delimiter.csv','small_file_delimiter.csv')
    for i in first():
        print(i)
