import zoo_create_reptile
import threading

if __name__ == '__main__':
    t2 = threading.Thread(target=zoo_create_reptile.open_sell)
    t2.start()