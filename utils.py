import json


def read_problem(path):
    data = {}
    try:
        with open(path, 'r') as f:
            data = json.load(f)
        if data:
            return (
                data.get("dim"), 
                data.get("fixCell"), 
                data.get("visible").get("left"), 
                data.get("visible").get("right"), 
                data.get("visible").get("top"), 
                data.get("visible").get("bottom"),
                data.get("constraintArea")
            )
    except Exception as e:
        print(e)