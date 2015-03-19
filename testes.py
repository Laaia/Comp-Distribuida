import hashlib
import xmlrpclib

a = {}

arq1 = "teste.txt"
arq2 = "teste2.txt"


a['hash1'] = arq1
a['hash2'] = arq2
a[arq1] = 'r'
a[arq2] = 'w'


print a.get(None)
