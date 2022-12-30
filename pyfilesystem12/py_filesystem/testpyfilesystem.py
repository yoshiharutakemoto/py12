from filesystem import FileSystem, Directory, MAX_BUF_FILE_SIZE, DIR_MAX_ELEMS
import pytest


@pytest.fixture
def filesystem() -> FileSystem:
    fs = FileSystem()
    fs.create_directory('.', "Dir_1")

    return fs


@pytest.fixture
def filesystem_complex() -> FileSystem:
    fs = FileSystem()
    fs.create_directory('.', "Dir_1")
    fs.create_directory('.', "Dir_2")
    fs.create_directory('.', "Dir_3")
    fs.create_directory('./Dir_1', "Dir_11")
    fs.create_directory('./Dir_1', "Dir_12")
    fs.create_directory('./Dir_2', "Dir_21")
    fs.create_directory('./Dir_2', "Dir_22")

    return fs


def test_filesystem_creation():
    '''Check if filesystem object is correctly initalized'''
    fs = FileSystem()
    
    assert fs.root.name == '~'
    assert fs.root.childs == []


def test_filesystem_create_directory():
    fs = FileSystem()
    fs.create_directory('.', "Dir_1")

    assert isinstance(fs.root.childs[0], Directory)
    assert fs.root.childs[0].name == "Dir_1"


def test_filesystem_create_multiple_directories():
    fs = FileSystem()
    fs.create_directory('.', "Dir_1")
    fs.create_directory('./Dir_1', "Nested_Dir")

    assert fs.root.childs[0].childs[0].name == "Nested_Dir"


def test_get_node(filesystem_complex: FileSystem):
    node = filesystem_complex.get_node("./Dir_1/Dir_12")

    assert isinstance(node, Directory)
    assert node.name == "Dir_12"


def test_string_to_path_complex_1():
    fs = FileSystem()
    fs.create_directory('.', "Dir_1")
    fs.create_directory('./Dir_1', "Nested_Dir")

    result = fs.string_to_path("./Dir_1/Nested_Dir")

    assert len(result) == 3
    assert result[0].name == "~"
    assert result[1].name == "Dir_1"
    assert result[2].name == "Nested_Dir"


def test_string_to_path_complex_2():
    fs = FileSystem()
    fs.create_directory('.', "Dir_1")
    fs.create_directory('./Dir_1', "Nested_Dir")

    result = fs.string_to_path(".")

    assert len(result) == 1
    assert result[0].name == "~"


def test_string_to_path_complex_3():
    fs = FileSystem()
    fs.create_directory('.', "LVL_0")
    fs.create_directory('./LVL_0', "LVL_1_1")
    fs.create_directory('./LVL_0', "LVL_1_2")
    fs.create_directory('./LVL_0/LVL_1_1', "LVL_2_1")
    fs.create_directory('./LVL_0/LVL_1_2', "LVL_2_2")

    result = fs.string_to_path("./LVL_0/LVL_1_1/../LVL_1_2/LVL_2_2")

    assert len(result) == 4
    assert result[0].name == "~"
    assert result[1].name == "LVL_0"
    assert result[2].name == "LVL_1_2"
    assert result[3].name == "LVL_2_2"


def test_create_binary_file(filesystem: FileSystem):
    file = filesystem.create_binary_file("./Dir_1", "file.bin", "Dummy info")

    assert filesystem.root.childs[0].childs[0].name == "file.bin"
    assert filesystem.root.childs[0].childs[0].information == "Dummy info"


def test_create_log_file(filesystem: FileSystem):
    file = filesystem.create_log_file("./Dir_1", "file.log", "Log info")

    assert filesystem.root.childs[0].childs[0].name == "file.log"
    assert filesystem.root.childs[0].childs[0].information == "Log info"


def test_create_buffer(filesystem: FileSystem):
    file = filesystem.create_buffer("./Dir_1", "file.buf")

    assert filesystem.root.childs[0].childs[0].name == "file.buf"
    assert len(filesystem.root.childs[0].childs[0].items) == 0


def test_delete(filesystem_complex: FileSystem):
    filesystem_complex.create_buffer("./Dir_1/Dir_11", "dummy.buf")

    buffer_file = filesystem_complex.get_node("./Dir_1/Dir_11/dummy.buf")
    folder = filesystem_complex.get_node("./Dir_1/Dir_11")

    assert(len(folder.childs) == 1)
    buffer_file.delete()
    assert(len(folder.childs) == 0)


def test_delete_2(filesystem_complex: FileSystem):
    filesystem_complex.create_buffer("./Dir_1/Dir_11", "dummy.buf")
    filesystem_complex.create_log_file("./Dir_1/Dir_11", "1.log")
    filesystem_complex.create_log_file("./Dir_1/Dir_11", "2.log")
    filesystem_complex.create_log_file("./Dir_1/Dir_11", "3.log")

    target = filesystem_complex.get_node("./Dir_1/Dir_11/2.log")
    folder = filesystem_complex.get_node("./Dir_1/Dir_11")

    assert(len(folder.childs) == 4)
    target.delete()
    assert(len(folder.childs) == 3)
    assert(target not in folder.childs)


def test_move(filesystem_complex: FileSystem):
    filesystem_complex.create_buffer("./Dir_1/Dir_11", "dummy.buf")
    buffer_file_folder = filesystem_complex.get_node("./Dir_1/Dir_11")
    buffer_file_folder.move("dummy.buf", "./Dir_3")

    original_folder = filesystem_complex.get_node("./Dir_1/Dir_11")
    destination_folder = filesystem_complex.get_node("./Dir_3")

    assert len(original_folder.childs) == 0
    assert len(destination_folder.childs) == 1
    assert destination_folder.childs[0].name == "dummy.buf"


def test_binary_file_read(filesystem_complex: FileSystem):
    filesystem_complex.create_binary_file("./Dir_1/Dir_11", "dummy.bin", "some info")
    bin_file = filesystem_complex.get_node("./Dir_1/Dir_11/dummy.bin")

    assert (bin_file.read() == "some info")


def test_log_file_read(filesystem_complex: FileSystem):
    filesystem_complex.create_log_file("./Dir_1/Dir_11", "dummy.log", "some info")
    log_file = filesystem_complex.get_node("./Dir_1/Dir_11/dummy.log")
    log_file.append("\nsome more info")

    assert (log_file.read() == "some info\nsome more info")


def test_buffer_file_push(filesystem_complex: FileSystem):
    filesystem_complex.create_buffer("./Dir_1/Dir_11", "dummy.buf")
    buffer = filesystem_complex.get_node("./Dir_1/Dir_11/dummy.buf")

    assert len(buffer.items) == 0

    buffer.push(1)
    buffer.push(2)
    buffer.push(3)

    assert len(buffer.items) == 3


def test_exception_path(filesystem_complex: FileSystem):
    with pytest.raises(ValueError):
        filesystem_complex.get_node("./Dir_1/Dir_11/../Dir_22")


def test_exception_buffer_max_elements(filesystem: FileSystem):
    buffer = filesystem.create_buffer(".", "dummy.buf")

    for _ in range(MAX_BUF_FILE_SIZE):
        buffer.push(1)

    with pytest.raises(ValueError):
        buffer.push(1)


def test_exception_directory_unique_name(filesystem: FileSystem):
    filesystem.create_directory(".", "Dummy")

    with pytest.raises(ValueError):
        filesystem.create_directory(".", "Dummy")


def test_exception_directory_max_elements(filesystem: FileSystem):
    for i in range(DIR_MAX_ELEMS-1):
        filesystem.create_directory(".", "Dir__"+str(i))

    with pytest.raises(ValueError):
        filesystem.create_directory(".", "Dummy")
