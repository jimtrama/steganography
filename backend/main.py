import os
from flask import Flask, request, jsonify, send_file
from utils import text_to_binary, text_to_length_prefixed_binary, encode, decode, cors, pvd_encode, pvd_decode, dct_encode, dct_decode
from settings import UPLOAD_FOLDER


app = Flask(__name__)
@app.route('/upload',methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    file_path = os.path.join(UPLOAD_FOLDER, 'file.png')
    file.save(file_path)

    return cors(jsonify({'message': 'File uploaded successfully','status':'ok'}))


@app.route('/get-file', methods=['GET'])
def get_image():
    file_path = os.path.join(UPLOAD_FOLDER, 'encoded.png')
    return cors(send_file(file_path, mimetype='image/png'))

@app.route('/decode', methods=['GET'])
def decode_file():
    msg = decode()
    return cors(jsonify({'message':msg}))

@app.route('/encode', methods=['GET'])
def encode_file():
    msg = request.args.get('msg')
    binary = text_to_binary(msg+"/")
    encode(binary)
    return cors(jsonify({'status':'ok'}))

@app.route('/encode-pvd', methods=['GET'])
def encode_file_pvd():
    msg = request.args.get('msg')
    binary = text_to_length_prefixed_binary(msg)
    try:
        pvd_encode(binary)
        return cors(jsonify({'status':'ok'}))
    except ValueError as error:
        return cors(jsonify({'status':'error', 'message': str(error)})), 400

@app.route('/encode-dct', methods=['GET'])
def encode_file_dct():
    msg = request.args.get('msg')
    dct_encode(msg)
    return cors(jsonify({'status':'ok'}))
@app.route('/decode-dct', methods=['GET'])
def decode_file_dct():
    msg = dct_decode()
    return cors(jsonify({'message': msg}))
@app.route('/decode-pvd', methods=['GET'])
def decode_file_pvd():
    msg = pvd_decode()
    return cors(jsonify({'message': msg}))

if __name__ == '__main__':
    app.run()
