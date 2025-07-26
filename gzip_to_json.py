import base64
import gzip
import json

# The input string provided
encoded_string = "H4sIAKgZhWgC/4XOwQrDIAyA4XufQjyLJGoS66uMHcoYXaG0l8IOw3eftzoHNqcc8vHnNqgyH73uj+lY9k2nsk+HTujsKCxGr9usk4glQZ+N0u/nMr/KgQIr2fS4J3dydoEazn0uMVQ8QGx47PPIcHLx1NaFLvLIVR4Ct99feOKx6gNi60Pfo9R95+XHo4UO9xbAIVWe//qO8nD/AhhKywz/AQAA"

# 1. Decode the Base64 string into bytes
compressed_bytes = base64.b64decode(encoded_string)

# 2. Decompress the Gzip bytes
json_bytes = gzip.decompress(compressed_bytes)

# 3. Decode the bytes to a UTF-8 string
json_string = json_bytes.decode('utf-8')

# To make the final output readable, we can load it into a Python object
# and then "pretty-print" it.
data = json.loads(json_string)
pretty_json = json.dumps(data, indent=2)

print(pretty_json)