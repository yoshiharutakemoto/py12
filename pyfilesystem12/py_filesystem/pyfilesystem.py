from __future__ import annotations
from typing import Any


DIR_MAX_ELEMS = 10
MAX_BUF_FILE_SIZE = 15
DELIMITER = '/'


class FileSystem():
    def __init__(self):
        self.root = Directory(self, path=[], name="~")
        self.cwd = self.root

    def change_working_directory(self, path):
        dest = self.get_node(path)
        
        if not isinstance(dest, Directory):
            raise ValueError("Destination is not a directory")

        self.cwd = dest

    def print_cwd(self):
        for c in self.cwd.childs:
            print(c)

    def string_to_path(self, string: str) -> list[Node]:
        return [self.cwd] + self.cwd.string_to_path(string, [])

    def path_to_string(self, path: list[Node]) -> str:
        return DELIMITER.join(path)

    def get_node(self, path) -> Node:
        return self.cwd.get_node_helper(path)

    def create_directory(self, path: str, name: str) -> Directory:
        dest_dir = self.get_node(path)
        return dest_dir.create_directory(name)

    def create_binary_file(self, path: str, name: str, information: str) -> BinaryFile:
        dest_dir = self.get_node(path)
        return dest_dir.create_binary_file(name, information)

    def create_log_file(self, path: str, name: str, information: str = None) -> LogFile:
        dest_dir = self.get_node(path)
        return dest_dir.create_log_file(name, information)

    def create_buffer(self, path: str, name: str) -> BufferFile:
        dest_dir = self.get_node(path)
        return dest_dir.create_buffer(name)

    def print_elements(self) -> None:
        print(self.cwd.name)
        self.cwd.print_elements(lvl=0)


class Node():
    def __init__(self, path: list[Node], name: str):
        self.path = path
        self.name = name

    def delete(self):
        parent = self.path[-1]
        parent.childs.pop(parent.childs.index(self))


class Directory(Node):
    def __init__(self, fs: FileSystem, path: list[Node], name: str):
        if DELIMITER in name:
            raise ValueError(f"Directory name contains {DELIMITER}")

        super().__init__(path, name)
        self.childs = []
        self.fs = fs

    def __repr__(self):
        return f"<DIR | Path: {DELIMITER.join([d.name for d in self.path]) if self.path else ''}/[ {self.name} ]>"

    def move(self, filename: str, destination: str):
        dest_dir = self.fs.get_node(destination)

        target = None

        for c in self.childs:
            if c.name == filename:
                target = c

        if target is None:
            raise ValueError("File does not exist")
        
        if not dest_dir or not isinstance(dest_dir, Directory):
            raise ValueError("Wrong destination path")

        self.childs.remove(target)
        dest_dir.childs.append(target)

    def can_create_file(self, new_file_name: str) -> bool:
        if len(self.childs) == DIR_MAX_ELEMS:
            raise ValueError(f"Directory can't contain more than {DIR_MAX_ELEMS} nodes")

        for child in self.childs:
            if child.name == new_file_name:
                raise ValueError("File with that name already exists!")

        return True

    def create_directory(self, name: str) -> Directory:
        self.can_create_file(name)
        self.childs.append(Directory(self.fs, self.path + [self], name))

    def create_binary_file(self, name: str, information: str) -> BinaryFile:
        self.can_create_file(name)

        file = BinaryFile(self.path + [self], name, information)
        self.childs.append(file)

        return file


    def create_log_file(self, name: str, information: str = None) -> LogFile:
        self.can_create_file(name)

        file = LogFile(self.path + [self], name, information)
        self.childs.append(file)

        return file

    def create_buffer(self, name: str) -> BufferFile:
        self.can_create_file(name)

        file = BufferFile(self.path + [self], name)
        self.childs.append(file)

        return file

    def print_elements(self, lvl=0) -> None:
        for child in self.childs:
            print("   "*(lvl+1) + child.name)
            
            if isinstance(child, Directory):
                child.print_elements(lvl+1)

    def string_to_path(self, string: str, path: list[Node]) -> list[Node]:
        print(f"string_to_path | {string} || {path}")
        if len(string) == 0:
            return path

        string_split = [s.strip() for s in string.split(DELIMITER)]
        search_node = string_split[0]

        if search_node == "..":
            path.pop()
            return self.path[-1].string_to_path('/'.join(string_split[1:]), path)

        elif search_node == "~":
            path = [self.path[0]]
            return self.path[0].string_to_path('/'.join(string_split[1:]), path)
        
        elif search_node == '.':
            return self.string_to_path('/'.join(string_split[1:]), path)

        for node in self.childs:
            if node.name == search_node:
                if not isinstance(node, Directory):
                    raise ValueError("Destination is not a directory")

                path.append(node)
                return node.string_to_path('/'.join(string_split[1:]), path)

        raise ValueError("Wrong path")

    def get_node_helper(self, path):
        target_dir_name = path.split(DELIMITER)[0]
        target = None

        if target_dir_name == '.':
            target = self
        elif target_dir_name == '..':
            target = self.path[-1]
        elif target_dir_name == '~':
            target = self.fs.root

        for c in self.childs:
            if c.name == target_dir_name:
                target = c

        if target is None:
            raise ValueError("Wrong path")

        if DELIMITER in path:
            return target.get_node_helper(DELIMITER.join(path.split(DELIMITER)[1:]))
        else:
            return target


class BinaryFile(Node):
    def __init__(self, path: list[Node], name: str, information: str):
        if DELIMITER in name:
            raise ValueError(f"BinaryFile name contains {DELIMITER}")
            
        super().__init__(path, name)
        self.information = information

    def __repr__(self):
        return f"<BIN | Path: {DELIMITER.join([d.name for d in self.path]) if self.path else ''}/[ {self.name} ]>"

    def read(self) -> None:
        return self.information


class LogFile(Node):
    def __init__(self, path: list[Node], name: str, information: str = ""):
        if DELIMITER in name:
            raise ValueError(f"LogFile name contains {DELIMITER}")
            
        super().__init__(path, name)
        self.information = information

    def __repr__(self):
        return f"<LOG | Path: {DELIMITER.join([d.name for d in self.path]) if self.path else ''}/[ {self.name} ]>"

    def read(self) -> str:
        return self.information

    def append(self, information: str) -> str:
        self.information += information


class BufferFile(Node):
    def __init__(self, path: list[Node], name: str):
        if DELIMITER in name:
            raise ValueError(f"BufferFile name contains {DELIMITER}")
            
        super().__init__(path, name)
        self.items = []

    def __repr__(self):
        return f"<BUF | Path: {DELIMITER.join([d.name for d in self.path]) if self.path else ''}/[ {self.name} ]>"

    def push(self, element: Any) -> bool:
        if len(self.items) == MAX_BUF_FILE_SIZE:
            raise ValueError("BufferFile size reached limit")

        self.items.append(element)

    def pop(self) -> bool:
        if len(self.items) == 0:
            raise ValueError("Can't get items from an empty BufferFile")

        return self.items.pop()
