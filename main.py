import ivyhandler as ivyh
import json

config = "."

with open("config.json", "r") as data:
    config = json.load(data)

print(config["llms"]["gemma-3"]["url"])
print(ivyh.completion(config["llms"]["gemma-3"]["url"], "Bu nerenin bayrağı", "./testdata/tr.jpg"))