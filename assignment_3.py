'''
1) Create a list of “person” dictionaries with a name, 
age and list of hobbies for each person. 
Fill in any data you want.

2) Use a list comprehension to convert this list 
of persons into a list of names (of the persons).

3) Use a list comprehension 
to check whether all persons are older than 20.

4) Copy the person list such that you can safely edit the name 
of the first person (without changing the original list).

'''

people_dict = [
    {
        'age': 40,
        'name': 'Bob',
        'hobbies': ["WindSurfing", "Grilling", "Dancing"]
    },
    {
        'age': 560,
        'name': 'Dracula',
        'hobbies': ["CastleBuilding", "Hunting", "History"]
    },
    {
        'age': 2,
        'name': 'Baby',
        'hobbies': ["Existing", "Eating", "Sleeping"]
    }
]

names_list = [person["name"] for person in people_dict]

print(names_list)

over_20_names_list = all([person["age"] > 20
                          for person in people_dict])

print(over_20_names_list)

safe_list = [person.copy() for person in people_dict]

safe_list[0]["name"] = "NotBob"

names_list = [person["name"] for person in people_dict]

print("After Mutation")
print(names_list)
