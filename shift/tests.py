# from django.test import TestCase

calendar = {
    "a":{"1":1},
    "b":{"2":2},
}

calendar2 = {
    "a":{
        "b": 1,
        "d": 2
    }
}

x = {
    "x":5
}
calendar2["a"]["e"] = 4



print(calendar["a"]["1"])
print(calendar2["a"]["b"])
print(calendar2)

# Create your tests here.
