import base64

from flask import Flask, jsonify,request, redirect, url_for
import time
import requests
import bs4

import cv2
import numpy as np
import os
from random import shuffle
from tqdm import tqdm

from keras.models import Sequential
from keras.layers import *
from keras.optimizers import *

def machine_learning():
    traindata = 'C:/Users/pjy41/Downloads/What-can-you-bring--main/What-can-you-bring--main/Train'

    cls = ['knife', 'cigarette lighter', 'Ammunition',
           'Dry batteries', 'Power Charger']

    def checklabel(img):
        label = img.split('.')[0]
        if label[:len(cls[0])] == 'knife':  # knife
            lb = np.array([1, 0, 0, 0, 0])
        elif label[:len(cls[1])] == 'cigarette lighter':  # cigarette lighter
            lb = np.array([0, 1, 0, 0, 0])
        elif label[:len(cls[2])] == 'Ammunition':  # Ammunition
            lb = np.array([0, 0, 1, 0, 0])
        elif label[:len(cls[3])] == 'Dry batteries':  # Dry batteries
            lb = np.array([0, 0, 0, 1, 0])
        elif label[:len(cls[4])] == 'Power Charger':  # Power Charger
            lb = np.array([0, 0, 0, 0, 1])
        else:
            lb = np.array([0, 0, 0, 0, 0])
        return lb

    def train():
        train_images = []
        for i in tqdm(os.listdir(traindata)):
            path = os.path.join(traindata, i)
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            img = cv2.resize(img, (64, 64))
            train_images.append([np.array(img), checklabel(i)])
        shuffle(train_images)
        return train_images


    training_images = train()
    tr_img_data = np.array([i[0] for i in training_images]).reshape(-1, 64, 64, 1)
    tr_lbl_data = np.array([i[1] for i in training_images])
    model = Sequential()

    model.add(InputLayer(input_shape=[64, 64, 1]))
    model.add(Conv2D(filters=32, kernel_size=5, strides=1, padding='same', activation='swish'))
    model.add(MaxPool2D(pool_size=5, padding='same'))

    model.add(Conv2D(filters=50, kernel_size=5, strides=1, padding='same', activation='swish'))
    model.add(MaxPool2D(pool_size=5, padding='same'))

    model.add(Conv2D(filters=80, kernel_size=5, strides=1, padding='same', activation='swish'))
    model.add(MaxPool2D(pool_size=5, padding='same'))

    model.add(Dropout(0.25))
    model.add(Flatten())
    model.add(Dense(128, activation='swish'))
    model.add(Dropout(rate=0.5))
    model.add(Dense(len(cls), activation='softmax'))
    optimizer = Adam(lr=1e-3)

    model.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics=['accuracy'])
    model.fit(x=tr_img_data, y=tr_lbl_data, epochs=100, batch_size=100, verbose=0)
    model.fit(x=tr_img_data, y=tr_lbl_data, epochs=10, batch_size=100)




    img = cv2.imread('somthing.jpg')
    data = img.reshape(1, 64, 64, 1)
    model_out = model.predict([data])

    if np.argmax(model_out) == 0:
        str_label = 'knife'
    elif np.argmax(model_out) == 1:
        str_label = 'lighter'
    elif np.argmax(model_out) == 2:
        str_label = 'Ammunition'
    elif np.argmax(model_out) == 3:
        str_label = 'Dry batteries'
    elif np.argmax(model_out) == 4:
        str_label = 'Power Charger'
    else:
        str_label = 'To be determined...'

    return str_label








def matchingElements(dictionary, searchString):
    return [key for key, value in dictionary.items() if searchString in key.lower()]

def get_results(search_term):
    url = "https://www.tsa.gov/travel/security-screening/whatcanibring/all-list"
    res = requests.get(url)
    soup = bs4.BeautifulSoup(res.text, 'lxml')
    items = soup.find('tbody')

    items_dic = {}

    for item in items.find_all('tr'):
        item_name = ""
        for item2 in item.find_all('td',{'class':'views-field views-field-nothing'}):
            item_name = item2.strong.text
            items_dic[item_name] = []

        for item3 in item.find_all('td', {'class': 'views-field views-field-field-carry-on-baggage'}):
            item_carry_on = item3.span.text
            items_dic[item_name].append(item_carry_on)
        for item4 in item.find_all('td', {'class': 'views-field views-field-field-checked-baggage'}):
            item_checked_bag = item4.span.text
            items_dic[item_name].append(item_checked_bag)
        for item2 in item.find_all('td', {'class': 'views-field views-field-nothing'}):
            if item2.find('p'):
                item_special_instruction = item2.p.text
                items_dic[item_name].append(item_special_instruction)

    found = matchingElements(items_dic, search_term)
    result = []
    for i in range(len(found)):
        items_dic[found[i]].insert(0, found[i])
        result.append(items_dic[found[i]])
    return result

app = Flask(__name__);
@app.route("/bot", methods=["POST"])
def response():
    query = dict(request.form)['query']
    if(query == "image"):
        res = machine_learning()
    else:
        query = get_results(query)
        count = len(query)
        if(count==0):
            res = "Can you please say one more time?" + "\n"
        elif(count==1):
            res = query[0][0] + "\n" + "Carry on Bags: " + query[0][1] + "\n" + "Chekced Bags: " + query[0][2] + "\n"
            if (query[0][3]):
                res = res + "\n" + "\n" + query[0][3]
        else:
            res = "Please choose the name of one of the listed items below:" + "\n"
            for i in range(count):
                res = res + str(i+1) + " " + query[i][0] + "\n"

    image_var = "Not Found Image, Please take a picture first..."
    return jsonify({"response" : res})


@app.route('/camera', methods=['POST'])
def camera():
    data = request.get_json(force=True)
    image_data = data['image']
    imgdata = base64.b64decode(image_data)

    # save image
    filename = 'something.jpg'
    with open(filename, 'wb') as f:
        f.write(imgdata)
        print("Image saved")

    image_var="knives"
    return "Success"

if __name__ == "__main__":
    app.run(debug=True)