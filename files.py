my_file = open('demo.txt', mode='r')
# my_file.write("WRITE WRITE \n")
# file_content = my_file.readlines()
# my_file.close()
# print(file_content)

# for line in file_content:
#     print(line[:-1])

file_ptr = my_file.readline()
# while loop critera

while file_ptr:
    file_ptr = my_file.readline()
    print(file_ptr)
