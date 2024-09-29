import xmlrpc.client, _json
import sys
import datetime
import requests

proxy = xmlrpc.client.ServerProxy("http://localhost:5002/api")
while True:
    
    print("Options:")
    print("1. Create Room")
    print("2. List Room")
    print("3. Update schedule manually")
    print("4. Update schedule via FenixAPI")
    print("q. Quit")
    action = input("Enter the number of the action you want to perform: ")
    
    if action == '1':
        
        room_name = input("Enter the room name: ")
        room_id = input("Enter the room ID: ")
        room_data = {"name": room_name, "id": room_id}
        data_to_send={'type':"room",'id': room_id}
        try:
            ret_1 = proxy.create_room(room_data)           
            response = requests.post(f"http://127.0.0.1:5011/API/generateqr",json=data_to_send)
            response.raise_for_status()
            
        except requests.RequestException as err:
            print(f"Error fetching data from QRAPI: {err}")
        except xmlrpc.client.ProtocolError as err:
            print("A protocol error occurred")
            print("URL: %s" % err.url)
            print("HTTP/HTTPS headers: %s" % err.headers)
            print("Error code: %d" % err.errcode)
            print("Error message: %s" % err.errmsg)
        except xmlrpc.client.Fault as err:
            print("RPC error occurred")
            print("Error code: %d" % err.faultCode)
            print("Error message: %s" % err.faultString)
    elif action == '2':
        try:
            rooms_list = proxy.list_rooms()
            print("Available Rooms:")
            for room_id, room_name in rooms_list:
                print(f"{room_id}. {room_name}")
            try:
                ret_2 = proxy.list_rooms()
                print(ret_2)
            except xmlrpc.client.ProtocolError as err:
                print("A protocol error occurred")
                print("URL: %s" % err.url)
                print("HTTP/HTTPS headers: %s" % err.headers)
                print("Error code: %d" % err.errcode)
                print("Error message: %s" % err.errmsg)
            except xmlrpc.client.Fault as err:
                print("RPC error occurred")
                print("Error code: %d" % err.faultCode)
                print("Error message: %s" % err.faultString)
        except xmlrpc.client.ProtocolError as err:
            print("A protocol error occurred")
            print("URL: %s" % err.url)
            print("HTTP/HTTPS headers: %s" % err.headers)
            print("Error code: %d" % err.errcode)
            print("Error message: %s" % err.errmsg)
        except xmlrpc.client.Fault as err:
            print("RPC error occurred")
            print("Error code: %d" % err.faultCode)
            print("Error message: %s" % err.faultString)
    elif action == '3':
        file_path = input("Enter the path to the JSON file: ")

        schedule_data = proxy.import_schedule_from_json(file_path)

        if schedule_data is not None:
            try:
                room_id = input("Enter the room ID: ")
                ret = proxy.update_room_schedule(room_id, schedule_data)
                print(ret)
            except xmlrpc.client.ProtocolError as err:
                print("A protocol error occurred")
                print("URL: %s" % err.url)
                print("HTTP/HTTPS headers: %s" % err.headers)
                print("Error code: %d" % err.errcode)
                print("Error message: %s" % err.errmsg)
            except xmlrpc.client.Fault as err:
                print("RPC error occurred")
                print("Error code: %d" % err.faultCode)
                print("Error message: %s" % err.faultString)
        else:
            print("Failed to load schedule data from the JSON file.")
    elif action == '4':

        room_id = input("Enter the room ID: ")
        current_date = datetime.datetime.now().strftime('%d/%m/%Y')

        url = f"https://fenix.tecnico.ulisboa.pt/api/fenix/v1/spaces/{room_id}?day={current_date}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            fenix_data = response.json()
            ret = proxy.update_room_schedule(room_id, fenix_data)
            print(ret)
        except requests.RequestException as err:
            print(f"Error fetching data from FenixAPI: {err}")
        except xmlrpc.client.ProtocolError as err:
            print("A protocol error occurred")
            print("URL: %s" % err.url)
            print("HTTP/HTTPS headers: %s" % err.headers)
            print("Error code: %d" % err.errcode)
            print("Error message: %s" % err.errmsg)
        except xmlrpc.client.Fault as err:
            print("RPC error occurred")
            print("Error code: %d" % err.faultCode)
            print("Error message: %s" % err.faultString)


    elif action.lower() == 'q':  
        print("Exiting the script. Goodbye!")
        sys.exit()  
