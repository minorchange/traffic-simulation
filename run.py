import time
from network.network_generation import network


if __name__ == "__main__":

    path = "maps/network_13x12.csv"
    n = network(path)

    for t in range(100):
        n.step()
        print(n)
        print()
        time.sleep(0.2)

    print()
