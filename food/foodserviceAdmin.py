import xmlrpc.client
import sys
import requests

proxy = xmlrpc.client.ServerProxy("http://localhost:5003/api")
while True:
    
    print("Options:")
    print("1. Create a restaurant")
    print("2. Create a menu item")
    print("3. List all restaurants")
    print("4. Show evaluations")
    print("q. Quit")
    action = input("Enter the number of the action you want to perform: ")
    
    if action == '1':

        restaurant_name = input("Enter the restaurant name: ")
    
        
        
        restaurante_id = input("Enter the room ID: ")
        restaurant_data = {"nome": restaurant_name, "id":restaurante_id}
        
        data_to_send={'type':"restaurant",'id': restaurante_id}
        
        try:
            ret_1 = proxy.create_restaurante(restaurant_data)
            print(ret_1)
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
            restaurant_list = proxy.list_restaurants()
            print("Available Restaurants:")
            for restaurant_id, restaurant_name in restaurant_list:
                print(f"{restaurant_id}. {restaurant_name}")

            restaurant_id = input("Enter the ID of the restaurant where you want to add a menu item: ")
            menu_prato = input("Enter the new menu data: ")

            menu_data = {"prato": menu_prato}
            
            try:
                ret_1 = proxy.create_menu(int(restaurant_id), menu_data)  
                
                print(ret_1)
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
        try:
            restaurant_list = proxy.list_restaurants()
            print("Available Restaurants:")
            for restaurant_id, restaurant_name in restaurant_list:
                print(f"{restaurant_id}. {restaurant_name}")

            try:
                ret_1 = proxy.list_restaurants()  
                
                print(ret_1)
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
    elif action == '4':           

        try:
            restaurant_list = proxy.list_restaurants()
            print("Available Restaurants:")
            for restaurant_id, restaurant_name in restaurant_list:
                print(f"{restaurant_id}. {restaurant_name}")

            restaurant_id = input("Enter the ID of the restaurant where you want to add a menu item: ")

            evaluations = proxy.list_evaluations(int(restaurant_id))
            print("Evaluations for Restaurant:")
            for evaluation in evaluations:
                print(evaluation)
                print("--------------------------------------------------------")

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