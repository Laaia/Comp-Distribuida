import hashlib
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer

log_arquivos = {}

def open_(arquivo, modo):
    print "Abrindo.."
    try:
        arq = open(arquivo, 'r')
    except IOError:
        print "Arquivo nao existe"
        return ""
    arq.close()
    m = hashlib.sha256()
    m.update(arquivo) #Atualiza hash

    log_arquivos[m.hexdigest()] = arquivo #Associa hash->arquivo
    log_arquivos[arquivo] = modo #Associa arquivo->modo de abertura

    return  m.hexdigest()

def read_(hash):
    print "Lendo..."
    retorno = ""
    arq = autenticar(hash, 'r')
    if arq is not None:
        retorno = arq.read()
        arq.close()
    return retorno


def write_(hash, texto):
    print "Escrevendo..."

    arq = autenticar(hash, 'w')
    if arq is not None:
        arq.write(texto)
        arq.close()
    return ""


def close_(hash):
    print "Fechando..."

    if hash in log_arquivos:
        arquivo = log_arquivos.get(hash)
        log_arquivos.pop(hash)
        log_arquivos.pop(arquivo)
        print "Arquivo fechado com sucesso!"
    else:
        print "Erro: Arquivo solicitado nao esta aberto.."

    return ""

def autenticar(hash, metodo):
    arquivo = log_arquivos.get(hash)
    modo = log_arquivos.get(arquivo)

    if (modo is not None) and (modo != metodo):
        print "Erro: Arquivo aberto em outro modo"
        return None

    try:
        arq = open(arquivo, modo)
    except IOError:
        print "Erro: Arquivo nao esta aberto"
        return None

    return arq

server = SimpleXMLRPCServer(("localhost", 8000))
print "Listening on port 8000..."

server.register_function(open_, "open_")
server.register_function(read_, "read_")
server.register_function(write_, "write_")
server.register_function(close_, "close_")

server.serve_forever()
