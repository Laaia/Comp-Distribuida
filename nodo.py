#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import xmlrpclib
import thread
import time
import sys
import socket

from SimpleXMLRPCServer import SimpleXMLRPCServer

log_arquivos = {}
know_peers = []

print "Serviço XML-RPC: "
iam = raw_input()
peer, host, port = iam.split()

print "Serviço UDP: "

UDP = raw_input()
hostUDP, portUDP = UDP.split()

class Server:

	def xopen(arquivo, modo):
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

	def xread(hash):
	    print "Lendo..."
	    retorno = ""
	    arq = autenticar(hash, 'r')
	    if arq is not None:
	        retorno = arq.read()
	        arq.close()
	    return retorno


	def xwrite(hash, texto):
	    print "Escrevendo..."

	    arq = autenticar(hash, 'w')
	    if arq is not None:
	        arq.write(texto)
	        arq.close()
	    return ""


	def xclose(hash):
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
	
	server = SimpleXMLRPCServer((host, int(port)))
	
	#regista funções que foram declaradas na classe no servidor
	server.register_function(xopen, "xopen")
	server.register_function(xread, "xread")
	server.register_function(xwrite, "xwrite")
	server.register_function(xclose, "xclose")


# Criação das threads


def doServer( threadName, self):
	print "\nServidor criado na porta " + port + "...\n"
	s = Server()					#Cria uma instância do servidor
	s.server.serve_forever() 		#Executa servidor para sempre

#Aqui fazemos o serviço de manipulação de arquivo do T1 pelo XML-RPC
def doClient( threadName, self):
	print "\nCliente criado ouvindo servidor na porta " + port + "...\n"
	proxy = xmlrpclib.ServerProxy("http://"+host+":"+port+"/")

	a = proxy.xopen('teste.txt', 'w')

#Método necessário para o T2
#Resposável por fazer a solicitação da tabela de peers conhecidos
def xgetPeers(threadName, self):
	msg = ''

	udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	dest = ('localhost', 54545)					#Endereço do local onde executa o serviço externo

	orig = (hostUDP, int(portUDP))				#Endereço de onde ouvirá a resposta do serviço externo
	udp.bind(orig)

	while 1:
		time.sleep(10)							#A cada 10 segundos:
		print "\nGetPeers..."
		udp.sendto (iam, dest) 					#Solicita serviço enviando seus dados

		while msg != '-1':						#Espera retorno da lista de peers conhecidos
			msg, cliente = udp.recvfrom(1024)

			if (msg != '-1' and msg != iam):
				if (msg in know_peers) == 0:		#Verifica se o peer ainda não foi registrado
					print "Atualização: " + msg
					know_peers.append(msg)			#registra peer	
		msg = ''
		print "Tabela de peers atualizada!"
try:
	thread.start_new_thread( doServer, ("Servidor", 2, ) )
	thread.start_new_thread( doClient, ("Cliente", 4, ) )
	thread.start_new_thread( xgetPeers, ("Get", 4, ) )
except:
	print "Error: unable to start thread"

while 1:
	pass
