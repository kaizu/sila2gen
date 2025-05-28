from my_first_server import Client
# from sila2.client import SilaClient as Client


def main():
    print("Starting SiLA Discovery...")

    client = Client.discover(insecure=True)
    # client = Client("172.21.0.3", 50052, insecure=True)

    print("Discovered SiLA Server with the following features:")
    for feature_identifier in client.SiLAService.ImplementedFeatures.get():
        print("-", feature_identifier)

    print(dir(client.MyFirstServer))
    print(client.MyFirstServer.PutItem)
    response1 = client.MyFirstServer.PutItem("spam", "ham", "eggs")
    print(response1)


if __name__ == "__main__":
    main()

