import json

def get_saved_consults():
    with open("consults.json", "r") as file:
        data = json.load(file)
    return data["saved"]

def save_consult(consult):
    with open("consults.json", "r") as file:
        data = json.load(file)
    data["saved"].append(consult)
    with open("consults.json", "w") as file:
        json.dump(data, file)

def delete_consult(consult_index):
    with open("consults.json", "r") as file:
        data = json.load(file)
    data["saved"].pop(consult_index)
    with open("consults.json", "w") as file:
        json.dump(data, file)

def clear_consults(key):
    with open("consults.json", "r") as file:
        data = json.load(file)
    data[key] = []
    with open("consults.json", "w") as file:
        json.dump(data, file)