import xmlrpclib

proxy = xmlrpclib.ServerProxy("http://localhost:8000/")

a = proxy.open_('teste.txt', 'w')
b = proxy.open_('teste2.txt', 'r')
proxy.write_(a, "Texto a ser escrito em a")
proxy.write_(b, "Texto a ser escrito em b") #Testar erros
proxy.close_(a)
a = proxy.open_('teste.txt', 'r')
proxy.read_(a)
proxy.close_(b)
proxy.close_(b) #Testar erros
