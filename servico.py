#!/usr/bin/env python
# -*- coding: utf-8 -*-

import thread
import socket


know_peers = [] #lista que conterá todos os peers conhecidos com os seus respectivos ip e porta

def xgetPeers(threadName, self):
	HOST = 'localhost' 
	PORT = 54545 
	msg = ''
	udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	orig = (HOST, PORT)
	udp.bind(orig)

	while 1:
		msg, cliente = udp.recvfrom(1024)	#Espera notificação de algum peer
		print("\n\nSolicitação de: " + msg)
		print "-------------------------------"
		
		dest = (str(cliente[0]), cliente[1]) # dest = (ip, porta) do UDP que enviou a msg

		if (msg in know_peers) == 0:		#Verifica se o peer ainda não foi registrado
			know_peers.append(msg)			#registra peer
			print "Adicionando: "+msg
		
		for p in know_peers:				#p = 'peer ip porta'
			msg = p
			udp.sendto (msg, dest)			#Envia lista para quem solicitou
		print "Tabela envida!"

		udp.sendto ('-1', dest)				#Sinaliza fim da entrega


try:
	thread.start_new_thread( xgetPeers, ("getPeers", 2, ) ) #criação da thread que rodará o serviço para os peers
except:
	print "Error: unable to start thread"

while 1:
	pass
