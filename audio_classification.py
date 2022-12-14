import json
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow import keras
import matplotlib.pyplot as plt
from random import randint

DATA_PATH = "./data.json"


def load_data(data_path):

    # ambil data json
    with open(data_path, "r") as fp:
        data = json.load(fp)

    # bagi data json menjadi dua
    X = np.array(data["mfcc"])
    y = np.array(data["labels"])
    return X, y


def plot_history(history):

    fig, axs = plt.subplots(2)

    # buat accuracy plot
    axs[0].plot(history.history["accuracy"], label="train accuracy")
    axs[0].plot(history.history["val_accuracy"], label="test accuracy")
    axs[0].set_ylabel("Accuracy")
    axs[0].legend(loc="lower right")
    axs[0].set_title("Accuracy eval")

    # buat error plot
    axs[1].plot(history.history["loss"], label="train error")
    axs[1].plot(history.history["val_loss"], label="test error")
    axs[1].set_ylabel("Error")
    axs[1].set_xlabel("Epoch")
    axs[1].legend(loc="upper right")
    axs[1].set_title("Error eval")

    plt.show()


def prepare_datasets(test_size, validation_size):

    # ambil data
    X, y = load_data(DATA_PATH)
    
    # membagi data train, validation and test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42
    )
    X_train, X_validation, y_train, y_validation = train_test_split(
        X_train, y_train, test_size=validation_size, random_state=42
    )

    # tambah dimensi satu lagi pada data
    X_train = X_train[..., np.newaxis]
    X_validation = X_validation[..., np.newaxis]
    X_test = X_test[..., np.newaxis]

    return X_train, X_validation, X_test, y_train, y_validation, y_test


def build_model(input_shape):

    # buat model jaringan
    model = keras.Sequential()

    # 1st conv layer
    model.add(keras.layers.Conv2D(32, (3, 3), activation="relu", input_shape=input_shape))
    model.add(keras.layers.MaxPooling2D((3, 3), strides=(2, 2), padding="same"))
    model.add(keras.layers.BatchNormalization())

    # 2nd conv layer
    model.add(keras.layers.Conv2D(32, (3, 3), activation="relu"))
    model.add(keras.layers.MaxPooling2D((3, 3), strides=(2, 2), padding="same"))
    model.add(keras.layers.BatchNormalization())

    # 3rd conv layer
    model.add(keras.layers.Conv2D(32, (2, 2), activation="relu"))
    model.add(keras.layers.MaxPooling2D((2, 2), strides=(2, 2), padding="same"))
    model.add(keras.layers.BatchNormalization())

    # flatten and dense layer
    model.add(keras.layers.Flatten())
    model.add(keras.layers.Dense(64, activation="relu"))
    model.add(keras.layers.Dropout(0.3))

    # output layer
    model.add(keras.layers.Dense(2, activation="softmax"))

    return model


def predict(model, X, y):

    # tambah dimensi satu lagi ke data
    X = X[np.newaxis, ...]

    # lakukan prediksi
    prediction = model.predict(X)

    # ambil nilai index
    predicted_index = np.argmax(prediction, axis=1)

    print("Target: {}, Predicted label: {}".format(y, predicted_index))


if __name__ == "__main__":

    # membagi semua dataset menjadi data train, validation, test
    X_train, X_validation, X_test, y_train, y_validation, y_test = prepare_datasets(
        0.3, 0.2
    )

    # buat jaringan CNN
    input_shape = (X_train.shape[1], X_train.shape[2], X_train.shape[3])
    model = build_model(input_shape)

    # compile model
    # Adam adalah algoritma optimasi pengganti untuk stochastic gradient descent untuk training model deep learning.
    # Adam menggabungkan sifat-sifat terbaik dari algoritma AdaGrad dan RMSProp untuk memberikan optimization algorithm
    # yang dapat menangani sparse gradients pada noisy problem.

    optimiser = keras.optimizers.Adam(learning_rate=0.0001)
    model.compile(
        optimizer=optimiser,
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    model.summary()

    # train model
    history = model.fit(
        X_train,
        y_train,
        validation_data=(X_validation, y_validation),
        batch_size=32,
        epochs=30,
    )

    # plot accuracy/error dari training dan validasi
    plot_history(history)

    # test model dengan data test
    test_loss, test_acc = model.evaluate(X_test, y_test, verbose=2)
    print("\nTest accuracy:", test_acc, "\n")

    # ambil sample dari test set untuk prediksi
    for i in range(10):
        r = randint(0, 140)
        X_to_predict = X_test[r]
        y_to_predict = y_test[r]
        # predict sample
        predict(model, X_to_predict, y_to_predict)

    # simpan model ke JSON
    model_json = model.to_json()
    with open("model.json", "w") as json_file:
        json_file.write(model_json)

    # simpan weights ke HDF5
    model.save_weights("model.h5")
    print("Saved model to disk")
