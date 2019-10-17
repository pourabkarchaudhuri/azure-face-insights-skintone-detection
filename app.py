import detect_skintone
import azure_face
from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
import time
import cv2
import base64
from PIL import Image
import numpy as np

def RGB2HEX(color):
    return "#{:02x}{:02x}{:02x}".format(int(color[0]), int(color[1]), int(color[2]))

dirname = os.path.dirname(__file__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
# Flask App Deifinition

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png'])
current_milli_time = lambda: int(round(time.time() * 1000))
@app.route('/detect', methods=['POST'])
def process_image():
    count = 0
    stamp = str(current_milli_time())
    # global model, classes, minsize, threshold, factor
    if not request.headers.get('Content-type') is None:
        if(request.headers.get('Content-type').split(';')[0] == 'multipart/form-data'):
            if 'image' in request.files.keys():
                print("Form Data, Multipart upload")
                file = request.files['image']
                # if user does not select file, browser also
                # submit a empty part without filename
                if file.filename == '':
                    result = {
                        "error":True,
                        "message": "No Image Recieved",
                        "gender":None,
                        "skin": None
                    }
                    return jsonify(result)
                # filename = secure_filename(file.filename)
                # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], "photo_"+stamp+".jpg"))

            else:
                return jsonify(get_status_code("Invalid body", "Please provide valid format for Image 2")), 415
        elif(request.headers.get('Content-type') == 'application/json'):
            if(request.data == b''):
                return jsonify(get_status_code("Invalid body", "Please provide valid format for Image")), 415
            else:
                print("Application/Json upload as base64")
                body = request.get_json()
                if 'image_string' in body.keys():
                    img_string = body['image_string']
                    try:
                        # str_image = img_string.split(',')[1]
                        imgdata = base64.b64decode(img_string)
                    
                        with open(os.path.join(UPLOAD_FOLDER, "photo_"+stamp+".jpg"), 'wb') as f:
                            f.write(imgdata)
                        
                    except IndexError:
                        result = {
                            "error":True,
                            "message": "Invalid base64 string",
                            "gender":None,
                            "skin": None
                        }
                        return jsonify(result)
                    
                    
                    
                else:
                    result = {
                        "error":True,
                        "message": "Put 'image_string' as key in input payload",
                        "gender":None,
                        "skin": None
                    }
                    return jsonify(result)

        else:
            return jsonify(get_status_code("Invalid header", "Please provide correct header with correct data")), 415
    
    else:
        return jsonify(get_status_code("Invalid Header", "Please provide valid header")), 401



    # print("File to be processed : {}".format(os.path.join(UPLOAD_FOLDER, "photo_"+stamp+".jpg")))
    root_image = os.path.join(UPLOAD_FOLDER, "photo_"+stamp+".jpg")
    # root_image_data = cv2.imread(os.path.join(UPLOAD_FOLDER, "photo_"+stamp+".jpg"))
    root_image_data = Image.open(os.path.join(UPLOAD_FOLDER, "photo_"+stamp+".jpg")) 
    # root_image_data.show()
    if root_image is None:
        print("Could not read input image")
    
    # face_count = 0

    face_data = azure_face.face_insights(root_image)
    # print("Face Data : {}".format(face_data))
    # print("--------")
    # print(face_data['faceRectangle']))
    print("Count of Faces Detected : {}".format(len(face_data)))

    if(len(face_data) == 1):
        print(face_data[0]['faceRectangle'])
        # print(type(face_data['faceRectangle']))
        # x = int(face_data[0]['faceRectangle']['top'])
        # y = int(face_data[0]['faceRectangle']['left'])
        # w = int(face_data[0]['faceRectangle']['width'])
        # h = int(face_data[0]['faceRectangle']['height'])

        left = int(face_data[0]['faceRectangle']['left'])
        top = int(face_data[0]['faceRectangle']['top'])
        bottom = left + int(face_data[0]['faceRectangle']['height'])
        right = top + int(face_data[0]['faceRectangle']['width'])

        gender = face_data[0]['faceAttributes']['gender']
        # print("Y : {}, X: {}, H: {}, W:{}".format(y,x,h,w))
        
        # print("Gender Detected : {}".format(gender))
       
        area = (left, top, bottom, right)
        cropped_img = root_image_data.crop(area)
        # cropped_img.show()

        # root_image_data.show()
        count = count + 1
        # cropped_img.show()
        opencvImage = cv2.cvtColor(np.array(cropped_img), cv2.COLOR_RGB2BGR)
        # cv2.imwrite(os.path.join(os.getcwd(), 'uploads', "photo_"+stamp+".jpg"), sub_faces)
        # cropped_img.save(os.path.join(os.getcwd(), 'uploads', "photo_"+stamp+".jpg"))
    elif(len(face_data) > 1):
        print("Too Many faces detected")
        count = len(face_data)
    else:
        print("No faces detected")
        count = 0
            
    print("Count : {}".format(count))
    if(count == 0):
        result = {
            "error":True,
            "message": "No faces found",
            "gender":None,
            "skin": None
        }
    elif(count>1):
        result = {
            "error":True,
            "message": "Too many faces detected",
            "gender":None,
            "skin": None
        }
    else:
        # cropped_image_data = cv2.imread(os.path.join(UPLOAD_FOLDER, "photo_"+stamp+".jpg"))
        skin_tone = detect_skintone.get_skin_tone(opencvImage)
        # print(skin_tone)
        hex_colors = list()
        for element in skin_tone:
            # print(element['color'])
            obtained_hexcolor = RGB2HEX(element['color'])
            hex_colors.append(obtained_hexcolor)

        # print(hex_colors)

        result = {
            "error":False,
            "message":None,
            "gender": gender,
            "skin": hex_colors
        }
    
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3002)

