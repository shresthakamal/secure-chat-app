# Secure chat using Openssl and MITM attacks

**This project is a part of assignment series for Network Security (CS6903).**

In this project, we have created a secure chat server that demonstrates how `Alice` and `Bob` could chat with each other.

The porject also implements `Trudy` who is going to intercept the chat messages between `Alice` and `Bob` launching various MITM attacks.

## Project Tree

```
├── Alice
│   ├── alice.crt
│   ├── alice.csr
│   ├── alice_key.pem
│   └── alice_pub.pem
├── Bob
│   ├── bob.crt
│   ├── bob.csr
│   ├── bob_key.pem
│   ├── bob_pub.pem
│   ├── pub-bob_key.pem
│   ├── pub-root_key.pem
│   ├── root.crt
│   └── root.srl
├── Makefile
├── Root
│   ├── pub-root_key.pem
│   ├── root.crt
│   └── root_key.pem
├── secure_chat_app.py
├── secure_chat_interceptor.py
└── Trudy
    ├── Fake_Alice
    │   ├── fake_alice.crt
    │   ├── fake_alice.csr
    │   ├── fake_alice_key.pem
    │   ├── pub-fake_alice_key.pem
    │   ├── pub-root_key.pem
    │   ├── root.crt
    │   └── root.srl
    └── Fake_Bob
        ├── fake_bob.crt
        ├── fake_bob.csr
        ├── fake_bob_key.pem
        ├── pub-fake_bob_key.pem
        ├── pub-root_key.pem
        ├── root.crt
        └── root.srl
```

---

## Team Members

- [Pallavi Saxena](mailto:cs21mtech11020@iith.ac.in)
- [Pradhumn Kanase](mailto:cs21mtech11018@iith.ac.in)
- [Kamal Shrestha](mailto:cs21mtech16001@iith.ac.in)

---

## Setup

All the files mentioned in the above tree should be uploaded to the VM before the chat can be started.

Refer Appendix to generate the certificates.

### 1. Loading the files into the Virtual Machine (VM)</summary>

The following command is used to load the files into the VM:

1.1. To copy and individual file:

```python
    scp FILE_NAME/ <SERVER>@<IP_ADDRESS>
```

1.2. To copy an entire folder and its contents

```python
    scp -r FOLDER_NAME/ <SERVER>@<IP_ADDRESS>
```

### 2. Loading the files into the individual containers

1.1. Loading an individual file:

```python
    lxc file push FILE_PATH_IN_VM <CONAINER_NAME>/root/
```

1.2. Loading an entire folder:

```python
    lxc file push -r FOLDER_NAME/ <CONAINER_NAME>/root/
```

---

## Run Instructions

Now that we have all the files loaded into the individual containers, we will run the chat server and start communication.

<br>

### 1. Running Secure Chat Application (`secure_chat_app.py`)

<br>
1.1. Server Side Application Run

```python
    python3 secure_chat_app.py -s -p PORT_NAME
```

1.2. Client Side Application Run

```python
    python3 secure_chat_app.py -c <SERVER_NAME> -p PORT_NAME
```

<br>

### 2. Running Interceptor for Secure Chat Application (`secure_chat_interceptor.py`)

<br>

2.1. Running `Downgrade Attack`:

```python
    python3 secure_chat_interceptor.py -d <CLIENT_NAME> <SERVER_NAME> <PORT_NUMBER>
```

2.2. Running `Man in the Middle attack`:

```python
    python3 secure_chat_interceptor.py -m <CLIENT_NAME> <SERVER_NAME> <PORT_NUMBER>
```

### 3. MakeFile

For ease of execution of mutiple redundant commands one after another, we have aso created a `MakeFile` that makes command execution efficient:

**VM Executions:**

- **`make all`**: To copy all the required files to the VM

  Make sure that the name and IP of the VM is properly configured
    <details><summary> More </summary>

  - > `scp Makefile ns@192.168.51.115:`
  - > `scp -r Alice/ ns@192.168.51.115:`
  - > `scp -r Bob/ ns@192.168.51.115:`
  - > `scp -r Root/ ns@192.168.51.115:`
  - > `scp -r Trudy/ ns@192.168.51.115:`
  - > `scp secure_chat_app.py ns@192.168.51.115:`
  - > `scp secure_chat_interceptor.py ns@192.168.51.115:`
  - > `scp poison.py ns@192.168.51.115:`
  </details>

- **`make <CONTAINER_NAME>`**: Get inside the container

  - > `make alice1`

- **`make ns`**: To load all the files inside the containers

  Make sure that the name of the containers are correct in the VM and Makefile
    <details><summary> More </summary>

  - > `lxc file push Root/root.crt alice1/root/`
  - > `lxc file push Root/root.crt bob1/root/`
  - > `lxc file push Root/root.crt trudy1/root/`
  - > `lxc file push -r Alice/ alice1/root/`
  - > `lxc file push -r Bob/ bob1/root/`
  - > `lxc file push -r Trudy/ trudy1/root/`
  - > `lxc file push secure_chat_app.py alice1/root/`
  - > `lxc file push secure_chat_app.py bob1/root/`
  - > `lxc file push secure_chat_interceptor.py trudy1/root/`
  - > `lxc file push Makefile alice1/root/`
  - > `lxc file push Makefile bob1/root/`
  - > `lxc file push Makefile trudy1/root/`
    </details>

Before, running the chat server, make sure all the files are properly placed in each containers.

- **`make capturepackets`**: To capture all the packets in a pcap file from client side

  - > `lxc exec alice1 -- tcpdump -w packet.pcap`

- **`make pullpackets`**: Download captured packets into VM

  - > `lxc file pull alice1/root/packet.pcap`

- **`make nsclean`**: Remove all the copied files from VM
    <details><summary> More </summary>

  - > `rm -r Alice/`
  - > `rm -r Bob/`
  - > `rm -r Trudy/`
  - > `rm -r Root/`
  - > `rm secure_chat_app.py`
  - > `rm secure_chat_interceptor.py`
  - > `rm Makefile `
  - > `rm packet.pcap`
  </details>

**Container Executions:**

- **`make installroot`**: Install the root certificate inside a container

  - > `sudo cp root.crt /usr/local/share/ca-certificates`
  - > `sudo update-ca-certificates`

- **`make client`**: Run the client

  - > `python3 secure_chat_app.py -c bob1 -p 8075`

- **`make server`**: Run the server

  - > `python3 secure_chat_app.py -s -p 8075`

Let's run the man in the middle attacks:

- **`make downgrade`**: Initiate Downgrade attack

  - > `python3 secure_chat_interceptor.py -d alice1 bob1 8075`

- **`make mitm`**: Initiate Man in the Middle (MITM) attack

  - > `python3 secure_chat_interceptor.py -m alice1 bob1 8075`

Cleaning the containers:

**`make <CONTAINER_NAME>clean`**: Remove all the loaded files and restart

<details><summary> More </summary>

- > `make alice1clean`
- > `rm -r Alice/`
- > `rm root.crt`
- > `rm secure_chat_app.py`
- > `rm Makefile`
- > `rm packet.pcap`
</details>
<br>

---

## Appendix

<details><summary>Certificate Generation and Verifications</summary><br/>

1. Generate Root Certificate (EC-512)

```python
    openssl ecparam -name brainpoolP512r1 -genkey -noout -out root.pem
```

2. Generate RSA Keys

```python
    openssl genrsa -out alice.pem 2048
```

3. Generate the public key from private key

```python
    openssl rsa -in alice.pem -pubout -out alice_pub.pub
```

4. Generate Certificate Signing Request

```python
    openssl req -key alice.pem -new -out alice.csr
```

5. Verify a certificate Signining Request

```python
    openssl req -text -in alice.csr -noout -verify
```

6. Generating Digest for verifications

```python
    openssl dgst -sha1 -out alice.csr.dgst alice.csr
```

7. Signing the Digest with CSR

```python
   openssl pkeyutl -sign -in alice.csr.dgst -inkey alice.pem -out alice.csr.dgst.sign
```

8. Verify CSR with Digest

```python
    openssl pkeyutl -verify -sigfile alice.csr.dgst.sign -in alice.csr.dgst -inkey alice.pem -pubin
```

9. Generate a Self Signed Certificate

```python
    openssl req -key alice.pem -new -x509 -days 365 -out alice.crt
```

10. Sign Certificate using selfsigned CA

```python
    openssl x509 -req -CA CA.crt -CAkey CA.pem -in alice.csr -out alice.crt -days 365 -CAcreateserial
```

11. View Certificate

```python
    openssl x509 -text -noout -in alice.crt
```

12. Verify client certificate with CA's certificate

```python
    openssl verify -verbose -CAfile CA.crt alice.crt
```

</details>

--

<details><summary>Working with SSH servers</summary>

- To login to the VM allocated, type `ssh ns@192.168.51.xw` command.

</details>

--

<details><summary>Working with `lxc` containers</summary>

- To list out the containers inside the VM, use `lxc ls` command from inside the VM.

- To login to a container, use `lxc exec <containername>` bash command from inside the VM.

- To logout from the respective container use `exit` command.
</details>
