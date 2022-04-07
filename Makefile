all:
	scp Makefile ns@192.168.51.115:
	scp -r Alice/ ns@192.168.51.115:
	scp -r Bob/ ns@192.168.51.115:
	scp -r Root/ ns@192.168.51.115:
	scp -r Trudy/ ns@192.168.51.115:
	scp secure_chat_app.py ns@192.168.51.115:
	scp secure_chat_interceptor.py ns@192.168.51.115:
	scp poison.py ns@192.168.51.115:

ns:
	lxc file push Root/root.crt alice1/root/
	lxc file push Root/root.crt bob1/root/
	lxc file push Root/root.crt trudy1/root/
	lxc file push -r Alice/ alice1/root/
	lxc file push -r Bob/ bob1/root/
	lxc file push -r Trudy/ trudy1/root/
	lxc file push secure_chat_app.py alice1/root/
	lxc file push secure_chat_app.py bob1/root/
	lxc file push secure_chat_interceptor.py trudy1/root/
	lxc file push Makefile alice1/root/
	lxc file push Makefile bob1/root/
	lxc file push Makefile trudy1/root/

nsclean:
	rm -r Alice/
	rm -r Bob/
	rm -r Trudy/
	rm -r Root/
	rm secure_chat_app.py
	rm secure_chat_interceptor.py
	rm Makefile 
	rm packet.pcap

alice1clean:
	rm -r Alice/
	rm root.crt
	rm secure_chat_app.py
	rm Makefile
	rm packet.pcap

bob1clean:
	rm -r Bob/
	rm root.crt
	rm secure_chat_app.py
	rm Makefile

trudy1clean:
	rm -r Trudy/
	rm root.crt
	rm secure_chat_interceptor.py
	rm Makefile

installroot:
	sudo cp root.crt /usr/local/share/ca-certificates
	sudo update-ca-certificates

alice1:
	lxc exec alice1 bash

bob1:
	lxc exec bob1 bash

trudy1:
	lxc exec trudy1 bash

capturepackets:
	lxc exec alice1 -- tcpdump -w packet.pcap

pullpackets:
	lxc file pull alice1/root/packet.pcap .

client:
	python3 secure_chat_app.py -c bob1 -p 8075

server:
	python3 secure_chat_app.py -s -p 8075

downgrade:
	python3 secure_chat_interceptor.py -d alice1 bob1 8075

mitm:
	python3 secure_chat_interceptor.py -m alice1 bob1 8075

poison:
	python3 poison.py -p
	make ns

unpoison:
	python3 poison.py -up
	make ns