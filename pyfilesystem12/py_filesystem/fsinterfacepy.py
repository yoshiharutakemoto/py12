from filesystem import *

fs = FileSystem()

fs.create_directory(".", "Directory_1")
fs.create_directory("./Directory_1", "Directory_11")
fs.create_directory("./Directory_1/Directory_11", "Nested_Dir")
fs.create_directory("./Directory_1", "Directory_12")

fs.create_directory(".", "Directory_2")
fs.create_binary_file("./Directory_2", "Binary1", "Here you can save information")
fs.create_binary_file("./Directory_2", "Binary2", "Random string of text")

fs.create_directory(".", "Directory_3")
fs.create_buffer("./Directory_3", "Buffer1")
fs.create_log_file("./Directory_3", "Log1", "")
fs.get_node("./Directory_3/Log1").append("1 - Hello")
fs.get_node("./Directory_3/Log1").append("\n2 - World")

print("Enter [help] to display list of commands")
while True:
    command = input(f"{DELIMITER.join([d.name for d in fs.cwd.path] + [fs.cwd.name])} > ").split(" ")

    try:
        if command[0] == "help":
            print("""Command list:
    help - display this message
    cd [path] - change current working directory
    ls - list current directory files
    tree - print tree of current working directory

    move [source] [destination] - move file or folder from source to destination
    del [path] - delete file or folder
    read [path] - read binary file or logfile

    makedir [name] - make a directory
    makebin [name] [information] - make a binary file

    makelog [name] [information] - make a log file
    addlog [path_to_logfile] [information] - add information to a log file

    makebuf [name] - make a buffer file
    pushbuf [path_to_buffile] [information] - push information to a buffer file
    popbuf [path_to_buffile] - pop information from a buffer file
    """)

        if command[0] == "cd":
            fs.change_working_directory(command[1])

        elif command[0] == "ls":
            fs.print_cwd()

        elif command[0] == "tree":
            fs.print_elements()

        elif command[0] == "del":
            if len(command) != 2:
                raise ValueError("Wrong command pattern: del [path]")
            
            file = fs.get_node(command[1])
            file.delete()

        elif command[0] == "move":
            if len(command) != 3:
                raise ValueError("Wrong command pattern: move [source] [destination]")
            
            source = fs.get_node(command[1])
            source.path[-1].move(source.name, command[2])
            
        elif command[0] == "read":
            if len(command) != 2:
                raise ValueError("Wrong command pattern: read [path]")

            file = fs.get_node(command[1])

            if not isinstance(file, (LogFile, BufferFile, BinaryFile)):
                raise ValueError("Can't read that file")
            
            print(file.read())

        elif command[0] == "makedir":
            if len(command) != 2:
                raise ValueError("Wrong command pattern: makedir [name]")

            fs.cwd.create_directory(command[1])

        elif command[0] == "makebin":
            if len(command) < 3:
                raise ValueError("Wrong command pattern: makebin [name] [information]")

            fs.cwd.create_binary_file(command[1], ' '.join(command[2:]))

        elif command[0] == "makelog":
            if len(command) < 2:
                raise ValueError("Wrong command pattern: makelog [name] [information]")

            fs.cwd.create_log_file(command[1], ' '.join(command[2:]))

        elif command[0] == "addlog":
            if len(command) < 3:
                raise ValueError("Wrong command pattern: addlog [path_to_logfile] [information]")

            logfile = fs.get_node(command[1])

            if not isinstance(logfile, LogFile):
                raise ValueError("Can't find LogFile")
            
            logfile.append(' '.join(command[2:]))

        elif command[0] == "makebuf":
            if len(command) != 2:
                raise ValueError("Wrong command pattern: makebuf [name]")

            fs.cwd.create_buffer(command[1])

        elif command[0] == "pushbuf":
            if len(command) < 3:
                raise ValueError("Wrong command pattern: pushbuf [path_to_buffile] [information]")

            buffer_file = fs.get_node(command[1])

            if not isinstance(buffer_file, BufferFile):
                raise ValueError("Can't find BufferFile")

            buffer_file.push(' '.join(command[2:]))

        elif command[0] == "popbuf":
            if len(command) != 2:
                raise ValueError("Wrong command pattern: popbuf [path_to_buffile]")

            buffer_file = fs.get_node(command[1])
            
            if not isinstance(buffer_file, BufferFile):
                raise ValueError("Can't find BufferFile")

            print(buffer_file.pop())

        else:
            print("Wrong command. Type [help] to get list of commands")

    except ValueError as e:
        print("ERROR: " + str(e))