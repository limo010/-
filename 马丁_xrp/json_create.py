import json

def save_data(data, json_name, type):
    try:
        with open(json_name, type, encoding='utf-8') as file_obj2:
            json.dump(data, file_obj2, ensure_ascii=False)
            file_obj2.write("\n")
        file_obj2.close()
    except Exception as e:
        print(e)