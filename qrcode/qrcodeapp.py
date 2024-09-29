from flask import Flask, render_template, request, send_file
import qrcode
import json
import os
from flask import jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("QRCodeDisplay.html")

@app.route("/generateqr", methods=['POST'])
def generate_qr():
    type_ = request.form.get('type')
    id_ = request.form.get('id')
    
    data = {
        type_: id_
    }
    
    json_data = json.dumps(data)

    filename = f"files/{type_}_{id_}.png"  

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    qr.add_data(json_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img.save(filename)




    return send_file(filename)

@app.route("/API/generateqr", methods=['POST'])
def generate_qr_API():

    
    
    json_data = request.get_json()    
    type = json_data['type']
    id = json_data['id']
    data = {
        type: id
    }
    
    # Convert the data dictionary to a JSON string
    json_str = json.dumps(data, separators=(',', ':'))

    filename = f"files/{type}_{id}.png"  

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    qr.add_data(json_str)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img.save(filename)

    return jsonify({"message": "QR code created successfully!"})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5011, debug=True)
