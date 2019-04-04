import server


while True:
    handler = server.VConfigHandler()
    print("Servers handler is active".center(50, '-'))
    print("Select one of the options".center(50, '-'))
    print("1. Edit Server", "2. Delete Server", "3. Show Servers List", "4. Create a Server", "5. Exit the handler", sep='\n')

    option = input("Choose an option: ")
    if option == '1':
        print("ID List:", handler.ids)
        ids = int(input("Select one from above ID List: "))
        print("Select the attribute value you wanna change: ", ['name', 'port', 'work-folder'])
        change = input("Select from above List: ")
        value = input("Enter Value: ")
        handler.edit_server(ids, change, value)
    elif option == '2':
        print("ID List:", handler.ids)
        ids = int(input("Select one from above ID List: "))
        handler.delete_server(ids)
    elif option == '3':
        handler.show_servers()
    elif option == '4':
        name = input("Enter the Server name: ")
        port = input("Enter Port that you wanna run this server: ")
        www = input("Enter the Working folder: ")
        handler.create_server(name, port, www)
    elif option == '5':
        break
    else:
        print("Invalid Option, Try again!!")
    print("Restarting Server Handler".center(50, '-'))
print("Exiting server handler".center(50, '-'))



