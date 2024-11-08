Data = {"test":[],"test2":""}
Data["test"].append({5:6})
Data["test"].append({4:5})
for i in Data["test"]:
    print(f"--{i.keys()}--")