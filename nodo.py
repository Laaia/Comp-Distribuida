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

print "Serviço XML-RPC (peer, host, port): "
iam = raw_input()
peer, host, port = iam.split()

class Server:

	def autenticar(self, hash, metodo):
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
		arq = Server().autenticar(hash, 'r')

		if arq is not None:
			retorno = arq.read()
			arq.close()
		return retorno


	def xwrite(hash, texto):
		print "Escrevendo..."

		arq = Server().autenticar(hash, 'w')
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



	server = SimpleXMLRPCServer((host, int(port)))

	#regista funções que foram declaradas na classe no servidor
	server.register_function(xopen, "xopen")
	server.register_function(xread, "xread")
	server.register_function(xwrite, "xwrite")
	server.register_function(xclose, "xclose")


class Client:
	proxy = xmlrpclib.ServerProxy("http://"+host+":"+port+"/")

	def xopen(self, arq, t):
		retorno = []
		for line in know_peers:										#Para cada peer conhecido
			p, i, pt = line.split()									#Extrai peer, ip e porta
			proxy = xmlrpclib.ServerProxy("http://"+i+":"+pt+"/")	#Conecta com o servidor
			retorno.append(proxy.xopen(arq, t))									#Requisita abertura para o servidor
		
		if retorno.count(retorno[0]) != len(retorno):						#Valida retorno. 
			print "Erro de abertura!..."
			return ''

		return retorno[0]

	def xread(self, hash):
		retorno = []
		for line in know_peers:
			p, i, pt = line.split()
			proxy = xmlrpclib.ServerProxy("http://"+i+":"+pt+"/")

			retorno.append(proxy.xread(hash))								#Requisita leitura para o servidor e armazena retorno em lista

		if retorno.count(retorno[0]) != len(retorno):						#Valida retorno. Ocorrência do objeto difere da quantidade de objetos
			print "Erro de leitura!..."
			return ''

		return retorno[0]
		
	def xwrite(self, hash, texto):
		retorno = []
		for line in know_peers:
			p, i, pt = line.split()
			proxy = xmlrpclib.ServerProxy("http://"+i+":"+pt+"/")

			retorno.append(proxy.xwrite(hash, texto))						#Requisita escrita para o servidor

		if retorno.count(retorno[0]) != len(retorno):					#Valida retorno. Ocorrência do objeto difere da quantidade de objetos
			print "Erro de escrita!..."
		return ''

		return retorno[0]

	def xclose(self, hash):
		retorno = []
		for line in know_peers:										
			p, i, pt = line.split()
			proxy = xmlrpclib.ServerProxy("http://"+i+":"+pt+"/")

			retorno.append(proxy.xclose(hash))									#Requisita encerramento para o servidor

		if retorno.count(retorno[0]) != len(retorno):						#Valida retorno. Ocorrência do objeto difere da quantidade de objetos
			print "Erro de encerramento!..."
		return ''

		return retorno[0]

# Criação das threads

def doServer( threadName, self):
	print "\nServidor criado ouvindo clientes na porta " + port + "...\n"
	s = Server()					#Cria uma instância do servidor
	s.server.serve_forever() 		#Executa servidor para sempre

#Aqui fazemos o serviço de manipulação de arquivo do T1 pelo XML-RPC
def doClient( threadName, self):
	print "\nCliente criado na porta " + port + "...\n"
	client = Client()

	#Espera registrar na rede antes de requisitar manipulação de arquivos
	time.sleep(12)
	a = client.xopen('teste.txt', 'r')
	client.xread(a)
	client.xclose(a)

#Método necessário para o T2
#Resposável por fazer a solicitação da tabela de peers conhecidos
def xgetPeers(threadName, self):
	msg = ''

	udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	dest = ('localhost', 54545)					#Endereço do local onde executa o serviço externo

	tempo = 0

	while 1:
		time.sleep(10)						#A cada 10 segundos:
		print "\nGetPeers..."
		udp.sendto (iam, dest) 					#Solicita serviço enviando seus dados

		while msg != '-1':						#Espera retorno da lista de peers conhecidos
			msg, cliente = udp.recvfrom(1024)

			if (msg != '-1'):
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
