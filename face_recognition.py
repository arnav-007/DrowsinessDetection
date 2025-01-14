import pickle
import cv2
from Drowsiness import Drowsy
from datetime import datetime
from smptp import mailing
from utils import face_rects
from utils import face_encodings
from utils import nb_of_matches
from pymongo import MongoClient

# file = open("log.txt", "a") 

# load the encodings + names dictionary
with open("encodings.pickle", "rb") as f:
    name_encodings_dict = pickle.load(f)
    
video_cap = cv2.VideoCapture(1)

while True:
    _, frame = video_cap.read()
    # get the 128-d face embeddings for each face in the input frame
    encodings = face_encodings(frame)
    # this list will contain the names of each face detected in the frame
    names = []

    # loop over the encodings
    for encoding in encodings:
        # initialize a dictionary to store the name of the 
        # person and the number of times it was matched
        counts = {}
        # loop over the known encodings
        for (name, encodings) in name_encodings_dict.items():
            # compute the number of matches between the current encoding and the encodings 
            # of the known faces and store the number of matches in the dictionary
            counts[name] = nb_of_matches(encodings, encoding)
        # check if all the number of matches are equal to 0
        # if there is no match for any name, then we set the name to "Unknown"
        if all(count == 0 for count in counts.values()):
            name = "Unknown"
            cv2.imwrite("screenshot.png", frame)
            mailing('itsthechamp0074@gmail.com')
            # break
        # otherwise, we get the name with the highest number of matches
        else:
            name = max(counts, key=counts.get)           

        # add the name to the list of names
        names.append(name)
        
        # file.write(name)
            # file.write(datetime)
        # file.write(" ")
        # file.write(datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)"))
        # file.write("\n")
        # file.close()
        connection_string= "mongodb+srv://minor.p0qjtgg.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority "
        client = MongoClient(connection_string)
        db = client["log"]
        collection = db["names"]
        post = {"id":"name"}
        collection.insert_one(post)


        
    # loop over the `rectangles` of the faces in the 
    # input frame using the `face_rects` function
    for rect, name in zip(face_rects(frame), names):
        # get the bounding box for each face using the `rect` variable
        x1, y1, x2, y2 = rect.left(), rect.top(), rect.right(), rect.bottom()
        # draw the bounding box of the face along with the name of the person
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, name, (x1, y1 - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

    # show the output frame
    cv2.imshow("frame", frame)
    break
    # wait for 1 milliseconde and if the q key is pressed, we break the loop
    if cv2.waitKey(1) == ord('q'):
        break
    
# release the video capture and close all windows

video_cap.release()
cv2.destroyAllWindows()
Drowsy()
