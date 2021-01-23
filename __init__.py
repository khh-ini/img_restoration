import os
from flask import Flask, render_template, request, flash, redirect, url_for, session
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import base64

UPLOAD_FOLDER = './static/'
ALLOW_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key="img_restore"


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOW_EXTENSIONS


def img_restoration(img, mask):
    img_origin = cv2.imread(img)
    mask = cv2.imread(mask, 0)
    # Proses Inpainting
    restored = cv2.inpaint(img_origin, mask, 15, cv2.INPAINT_NS)

    cv2.imwrite("static/repaired.jpg", restored)
    _, img_encode = cv2.imencode('.jpg', restored)
    return base64.b64encode(img_encode)


def img_mask(img, threshold1, threshold2, kernel):
    # Load GrayScale Image
    marked_demages = cv2.imread(img, 0)

    # Merubah menjadi citra binary
    ret, thresh1 = cv2.threshold(marked_demages, threshold1, threshold2, cv2.THRESH_BINARY)
    # Memperbesar ukuran citra binary
    kernel = np.ones(kernel, np.uint8)
    # mask = cv2.dilate(thresh1, kernel, iterations=1)
    mask = cv2.morphologyEx(thresh1, cv2.MORPH_DILATE, kernel)
    cv2.imwrite("static/masking.jpg", mask)
    _, img_encode =  cv2.imencode('.jpg', mask)
    return base64.b64encode(img_encode)

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        session.pop("file", None)
        session.pop("thres1", None)
        session.pop("thres2", None)
        session.pop("kernel", None)

        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            session['file']=filename
            return redirect(url_for('hello_world', file=filename))

    if request.method == 'GET':
        if session is not None:
            return render_template('index.html',result=session)
        else:
            return render_template('index.html')


@app.route('/create_mask', methods=['POST'])
def create_mask():
    if request.method == 'POST':
        if request.form['file'] is not None and request.form['threshold1'] is not None and request.form['threshold2'] is not None and request.form['kernel'] is not None:
            session['thres1'] = request.form['threshold1']
            session['thres2'] = request.form['threshold2']
            session['kernel'] = request.form['kernel']
            tresh1 = int(request.form['threshold1'])
            tresh2 = int(request.form['threshold2'])
            kernel = request.form['kernel'].split(',')
            for i in range(len(kernel)):
                kernel[i] = int(kernel[i])
            kernel = tuple(kernel)
            mask = img_mask(os.path.join('static',request.form['file']), tresh1, tresh2, kernel)
            return redirect(url_for('hello_world', mask=mask))

@app.route('/restore_img', methods=['GET'])
def restore_img():
    restored = img_restoration(os.path.join('static',session['file']),'static/masking.jpg')
    return redirect(url_for('hasil', hasil=restored))


@app.route('/hasil', methods=['GET'])
def hasil():
    return render_template('hasil.html')

