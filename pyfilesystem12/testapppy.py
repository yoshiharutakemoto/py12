import pytest
from app import app
from python_filesystem.filesystem import FileSystem, Directory, BinaryFile, LogFile, BufferFile


@pytest.fixture
def app_fixture():
    fs = FileSystem()
    fs.create_directory(".", "dir1")
    fs.create_directory("./dir1", "dir11")
    fs.create_directory(".", "dir2")
    fs.create_directory(".", "dir3")

    app.config.update({
        "TESTING": True,
        "FILESYSTEM_OBJ": fs
    })

    return app.test_client()


def test_index_get(app_fixture):
    index_response = app_fixture.get("/")

    assert index_response.json == {"name": "~", "type": "directory", "path": [], "childs": ["dir1", "dir2", "dir3"]}


def test_file_get(app_fixture):
    index_response = app_fixture.get("/?path=./dir1")

    assert index_response.json == {"name": "dir1", "type": "directory", "path": ["~"], "childs": ["dir11"]}


def test_create_directory(app_fixture):
    response = app_fixture.post("/directory", data={"path": ".", "name": "dir_test"})
    dir_creates = app_fixture.get("/?path=./dir_test")

    assert response.status_code == 200
    assert dir_creates.json['name'] == "dir_test"
    assert dir_creates.json['type'] == "directory"


def test_create_binary(app_fixture):
    response = app_fixture.post("/binaryfile", data={"path": ".", "name": "bin_test", "information": "123"})
    dir_creates = app_fixture.get("/?path=./bin_test")

    assert response.status_code == 200
    assert dir_creates.json['name'] == "bin_test"
    assert dir_creates.json['type'] == "binary"


def test_create_logtextfile(app_fixture):
    response = app_fixture.post("/logtextfile", data={"path": ".", "name": "log_test"})
    dir_creates = app_fixture.get("/?path=./log_test")

    assert response.status_code == 200
    assert dir_creates.json['name'] == "log_test"
    assert dir_creates.json['type'] == "logfile"


def test_create_bufferfile(app_fixture):
    response = app_fixture.post("/bufferfile", data={"path": ".", "name": "buffer_test"})
    dir_creates = app_fixture.get("/?path=./buffer_test")

    assert response.status_code == 200
    assert dir_creates.json['name'] == "buffer_test"
    assert dir_creates.json['type'] == "buffer"


def test_move(app_fixture):
    app_fixture.post("/directory", data={"path": ".", "name": "d1"})
    app_fixture.post("/directory", data={"path": ".", "name": "d2"})
    app_fixture.post("/bufferfile", data={"path": "./d1", "name": "target"})

    response = app_fixture.put("/", data={"src": "./d1/target", "dest": "./d2"})

    assert response.status_code == 200
    assert response.json["name"] == "d2"
    assert "target" in response.json["childs"]
    

def test_delete(app_fixture):
    app_fixture.post("/directory", data={"path": ".", "name": "d1"})
    app_fixture.post("/bufferfile", data={"path": "./d1", "name": "target"})
    app_fixture.post("/bufferfile", data={"path": "./d1", "name": "target_1"})

    response_delete = app_fixture.delete("/", data={"path": "./d1/target"})
    response_check = app_fixture.get("/?path=./d1")

    assert response_delete.status_code == 200
    assert response_check.json['childs'] == ['target_1']


def test_binaryfile_read(app_fixture):
    app_fixture.post("/binaryfile", data={"path": ".", "name": "bf", "information": "hello world"})
    response = app_fixture.get("/binaryfile?path=./bf")

    assert response.status_code == 200
    assert response.data == b'hello world'


def test_logfile_read(app_fixture):
    app_fixture.post("/logtextfile", data={"path": ".", "name": "lf", "information": "hello log"})
    response = app_fixture.get("/logtextfile?path=./lf")

    assert response.status_code == 200
    assert response.data == b'hello log'


def test_logfile_append(app_fixture):
    app_fixture.post("/logtextfile", data={"path": ".", "name": "lf", "information": "hello log"})
    app_fixture.put("/logtextfile", data={"path": "./lf", "information": "\nmore info"})
    
    response = app_fixture.get("/logtextfile?path=./lf")

    assert response.status_code == 200
    assert response.data == b'hello log\nmore info'


def test_buffer_push(app_fixture):
    app_fixture.post("/bufferfile", data={"path": ".", "name": "bf"})
    app_fixture.put("/bufferfile", data={"path": "./bf", "information": "1"})
    app_fixture.put("/bufferfile", data={"path": "./bf", "information": "2"})
    app_fixture.put("/bufferfile", data={"path": "./bf", "information": "3"})

    response = app_fixture.get("/?path=./bf")

    assert response.json['type'] == "buffer"
    assert response.json['length'] == 3


def test_buffer_pop(app_fixture):
    app_fixture.post("/bufferfile", data={"path": ".", "name": "bf"})
    app_fixture.put("/bufferfile", data={"path": "./bf", "information": "1"})
    app_fixture.put("/bufferfile", data={"path": "./bf", "information": "2"})
    app_fixture.put("/bufferfile", data={"path": "./bf", "information": "3"})

    pop1 = app_fixture.get("/bufferfile?path=./bf")
    pop2 = app_fixture.get("/bufferfile?path=./bf")
    pop3 = app_fixture.get("/bufferfile?path=./bf")
    
    assert pop1.data == b"3"
    assert pop2.data == b"2"
    assert pop3.data == b"1"