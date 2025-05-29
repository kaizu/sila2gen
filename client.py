from dotenv import load_dotenv
load_dotenv()
from deck import put_item, new_consumable, consumables_state, spot_state

# from my_first_server import Client
from sila2.client import SilaClient as Client


def main():
    # Initial setup
    print(put_item("A", "3fa85f64-5717-4562-b3fc-2c963f66afa6", "plate96"))
    print(spot_state())
    print(new_consumable("RollA", 1000))
    print(consumables_state())

    # Connect to SiLA Server
    print("Starting SiLA Discovery...")

    client = Client.discover(insecure=True)
    # client = Client("172.21.0.3", 50052, insecure=True)

    print("Discovered SiLA Server with the following features:")
    for feature_identifier in client.SiLAService.ImplementedFeatures.get():
        print("-", feature_identifier)

    print(dir(client.MyFirstServer))
    print(client.MyFirstServer.PutItem)

    # Send a command
    response1 = client.MyFirstServer.PutItem("spam", "ham", "eggs")
    print(response1)

    # Check the final status
    print(consumables_state())


if __name__ == "__main__":
    main()
