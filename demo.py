import ivylib as ivyh
import json

config = "."

with open("config.json", "r") as data:
    config = json.load(data)

print(config["llms"]["dolphin-mistral-24b-venice-edition"]["by"])
print(config["llms"]["dolphin-mistral-24b-venice-edition"]["short"])
for chunk in ivyh.completion(config["llms"]["dolphin-mistral-24b-venice-edition"]["url"], """Make this code run faster: """):
    print(chunk, end='', flush=True)
print()