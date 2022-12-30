from flask import Flask, request, make_response
from python_filesystem.filesystem import FileSystem, DELIMITER
from python_filesystem.filesystem import BinaryFile, LogFile, BufferFile


fs = FileSystem()
app = Flask(__name__)
app.config["FILESYSTEM_OBJ"] = fs


@app.route("/", methods=["GET", "PUT", "DELETE"])
def index():
    app_fs = app.config["FILESYSTEM_OBJ"]

    if request.method == "GET":
        # Getting file information as json
        path = request.args.get("path", '.')

        try:
            node_to_response = app_fs.get_node(path)
        except ValueError:
            return make_response({"status": "error", "message": "Wrong path"}, 404)

        return node_to_response.to_json()

    elif request.method == "PUT":
        # Move command
        src = request.form.get("src")
        dest = request.form.get("dest")


        if not src or not dest:
            return make_response({"status": "error", "message": "You need to specify src and dest to move elements!"}, 400)

        src_folder_path = src[:src.rindex(DELIMITER)]
        src_filename = src[src.rindex(DELIMITER)+1:]

        try:
            src_folder = app_fs.get_node(src_folder_path)
            move_result = src_folder.move(src_filename, dest)

        except ValueError as e:
            return make_response({"status": "error", "message": str(e)}, 400)

        return move_result.to_json()

    elif request.method == "DELETE":
        # Delete command
        path = request.form.get("path")

        if path is None:
            return make_response({"status": "error", "message": "Argument path is required!"}, 400)

        try:
            target_node = app_fs.get_node(path)
            return target_node.delete().to_json()

        except ValueError as e:
            return make_response({"status": "error", "message": str(e)}, 400)


@app.route("/directory", methods=["POST"])
def directory():
    app_fs = app.config["FILESYSTEM_OBJ"]

    path = request.form.get("path")
    name = request.form.get("name")

    if not path or not name:
        return make_response({"status": "error", "message": "args path and name are required"}, 400)

    try:
        created_dir = app_fs.create_directory(path, name)
    except ValueError as e:
        return make_response({"status": "erorr", "message": str(e)}, 400)

    return make_response(created_dir.to_json(), 200)


@app.route("/binaryfile", methods=["GET", "POST"])
def binaryfile():
    app_fs = app.config["FILESYSTEM_OBJ"]

    if request.method == "GET":
        # Reading binary file
        path = request.args.get("path")

        if not path:
            return make_response({"status": "error", "message": "Argument path is required"}, 400)

        binary_file = app_fs.get_node(path)

        if not isinstance(binary_file, BinaryFile):
            return make_response({"status": "error", "message": "File is not BinaryFile"}, 400)

        return binary_file.read()


    elif request.method == "POST":
        # Creating binary file
        path = request.form.get("path")
        name = request.form.get("name")
        information = request.form.get("information")

        if not path or not name:
            return make_response({"status": "error", "message": "Arguments path and name are required"}, 400)

        if not information:
            return make_response({"status": "error", "message": "Argument information is required"}, 400)

        try:
            created_file = app_fs.create_binary_file(path, name, information)
        except ValueError as e:
            return make_response({"status": "erorr", "message": str(e)}, 400)

        return make_response(created_file.to_json(), 200)


@app.route("/logtextfile", methods=["GET", "POST", "PUT"])
def logtextfile():
    app_fs = app.config["FILESYSTEM_OBJ"]

    if request.method == "GET":
        # Reading log file
        path = request.args.get("path")

        if not path:
            return make_response({"status": "error", "message": "Argument path is required"}, 400)

        log_file = app_fs.get_node(path)

        if not isinstance(log_file, LogFile):
            return make_response({"status": "error", "message": "File is not BinaryFile"}, 400)

        return log_file.read()

    elif request.method == "PUT":
        path = request.form.get("path")
        information = request.form.get("information")

        if not path or not information:
            return make_response({"status": "error", "message": "Arguments path and information is required"}, 400)

        log_file = app_fs.get_node(path)

        if not isinstance(log_file, LogFile):
            return make_response({"status": "error", "message": "File is not BinaryFile"}, 400)

        log_file.append(information)

        return log_file.read()

    elif request.method == "POST":
        path = request.form.get("path")
        name = request.form.get("name")
        information = request.form.get("information")

        if not path or not name:
            return make_response({"status": "error", "message": "Arguments path and name are required"}, 400)

        try:
            created_file = app_fs.create_log_file(path, name, information)
        except ValueError as e:
            return make_response({"status": "erorr", "message": str(e)}, 400)

        return make_response(created_file.to_json(), 200)


@app.route("/bufferfile", methods=["GET", "PUT", "POST"])
def bufferfile():
    app_fs = app.config["FILESYSTEM_OBJ"]

    if request.method == "GET":
        path = request.args.get("path")

        if not path:
            return make_response({"status": "error", "message": "Argument path is required"}, 400)

        buffer_file = app_fs.get_node(path)

        if not isinstance(buffer_file, BufferFile):
            return make_response({"status": "error", "message": "File is not BufferFile"}, 400)

        try:
            return buffer_file.pop()
        except ValueError as e:
            return make_response({"status": "error", "message": str(e)}, 400)
    
    elif request.method == "PUT":
        path = request.form.get("path")
        information = request.form.get("information")

        if not path or not information:
            return make_response({"status": "error", "message": "Arguments path and information are required"}, 400)

        buffer_file = app_fs.get_node(path)

        if not isinstance(buffer_file, BufferFile):
            return make_response({"status": "error", "message": "File is not BufferFile"}, 400)

        buffer_file.push(information)

        return buffer_file.to_json()

    elif request.method == "POST":
        path = request.form.get("path")
        name = request.form.get("name")

        if not path or not name:
            return make_response({"status": "error", "message": "Arguments path and name are required"}, 400)

        try:
            created_file = app_fs.create_buffer(path, name)
        except ValueError as e:
            return make_response({"status": "erorr", "message": str(e)}, 400)

        return make_response(created_file.to_json(), 200)


if __name__ == "__main__":
    app.run(debug=True)
