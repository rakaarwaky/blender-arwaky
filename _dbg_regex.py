import re

KV = r'(?:(["\'])(?:\\.|[^"\'])*\2|[^"\'\s,]+)'
print("KV repr:", repr(KV))
full = r'(?i)(["\']?)(password)\1\s*[:=]\s*' + KV
print("FULL repr:", repr(full))
pat = re.compile(full)

# Test value branch alone
val = re.compile(r'(")(?:\\.|[^"\'])*\2')
print("val match \"hunter2\":", val.match('"hunter2"'))
print("val match \"my secret\":", val.match('"my secret"'))

print("full match \"password\": \"hunter2\":", pat.search('"password": "hunter2"'))
# step by step
p2 = re.compile(r'(?i)(["\']?)(password)\1')
print("key part search:", p2.search('"password": "hunter2"'))
# without optional quote + backref
p3 = re.compile(r'(?i)("?)(password)\1\s*[:=]\s*')
print("with quote? search:", p3.search('"password": "hunter2"'))
# try removing the key-quote symmetry
p4 = re.compile(r'(?i)["\']?password["\']?\s*[:=]\s*' + KV)
print("p4 sub:", p4.sub("[REDACTED]", 'config = {"password": "hunter2"}'))
