"""from smartcard.System import readers
from smartcard.Exceptions import NoReadersException


def get_nfc_uid() -> str | None:
    print("Waiting for NFC card...")

    try:
        available_readers = readers()
        if not available_readers:
            print("No smart card readers found.")
            return None

        reader = available_readers[0]
        print(f"Using reader: {reader}")

        connection = reader.createConnection()
        connection.connect()

        # APDU command to get UID
        GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
        data, sw1, sw2 = connection.transmit(GET_UID)

        if (sw1, sw2) == (0x90, 0x00):
            uid = ''.join(f'{byte:02x}' for byte in data)
            print(f"Card detected! UID: {uid}")
            return uid

        print(f"Failed to read UID. SW1={sw1:02X}, SW2={sw2:02X}")
        return None

    except NoReadersException:
        print("No ACR122U reader found.")
        return None
    except Exception as e:
        print(f"NFC error: {e}")
        return None


if __name__ == "__main__":
    uid = get_nfc_uid()
    if uid:
        print("Returned UID:", uid)
    else:
        print("No UID read.")"""


"""import nfc

def get_nfc_uid() -> str | None:
    print("waiting for nfc")

    try:
        with nfc.ContactlessFrontend("usb") as clf:
            uid_holder = {"uid": None}

            def on_connect(tag):
                uid = tag.identifier.hex()
                uid_holder["uid"] = uid
                print(f"card detected UID: {uid}")
                return False
            
            clf.connect(rdwr={"on-connect": on_connect})
            return uid_holder["uid"]
        
    except Exception as e:
        print(f"NFC error: {e}")
        return None
    
if __name__ == "__main__":
    uid = get_nfc_uid()
    if uid:
        print("returned UID", uid)
    else:
        print("no UID read")"""

from smartcard.System import readers
from smartcard.CardConnection import CardConnection
from smartcard.Exceptions import NoCardException, CardConnectionException
import time


def try_connect(reader):
    protocols = [
        CardConnection.T0_protocol,
        CardConnection.T1_protocol,
        CardConnection.RAW_protocol,
    ]

    last_error = None

    for proto in protocols:
        try:
            conn = reader.createConnection()
            conn.connect(protocol=proto)
            print(f"Connected with protocol: {proto}")
            return conn
        except Exception as e:
            last_error = e

    return None


def read_uid():
    print("Waiting for NFC card...")

    rlist = readers()
    if not rlist:
        print("No smart card readers found.")
        return None

    reader = rlist[0]
    print(f"Using reader: {reader}")

    while True:
        try:
            conn = try_connect(reader)

            if conn is None:
                print("No card detected yet...")
                time.sleep(1)
                continue

            # Get UID command for ACR122U
            apdu = [0xFF, 0xCA, 0x00, 0x00, 0x00]
            data, sw1, sw2 = conn.transmit(apdu)

            if sw1 == 0x90 and sw2 == 0x00:
                uid = "".join(f"{b:02X}" for b in data)
                print(f"Card detected UID: {uid}")
                return uid
            else:
                print(f"UID read failed: SW1={hex(sw1)} SW2={hex(sw2)}")
                time.sleep(1)

        except NoCardException:
            print("Please place card on reader...")
            time.sleep(1)

        except CardConnectionException as e:
            print(f"Card connection error: {e}")
            time.sleep(1)

        except Exception as e:
            print(f"Unexpected error: {e}")
            time.sleep(1)


if __name__ == "__main__":
    uid = read_uid()
    if uid:
        print(f"Returned UID: {uid}")
    else:
        print("No UID read.")