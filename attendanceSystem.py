import csv
import random

import cv2
import os
import face_recognition
import datetime
from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from connection import conn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from io import StringIO

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

known_faces = []
known_names = []

today = datetime.date.today().strftime("%d_%m_%Y")


def get_known_encodings():
    global known_faces, known_names
    known_faces = []
    known_names = []
    for filename in os.listdir('static/faces'):
        image = face_recognition.load_image_file(os.path.join('static/faces', filename))
        encoding = face_recognition.face_encodings(image)[0]
        known_faces.append(encoding)
        known_names.append(os.path.splitext(filename)[0])


def totalreg():
    return len(os.listdir('static/faces/'))


def extract_attendance():
    results = conn.read(f"SELECT * FROM {today}")
    return results


def mark_attendance(person):
    name = person.split('_')[0]
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    user = conn.read("SELECT id, email FROM users WHERE name = %s", (name,))
    if user:
        user_id = user[0][0]
        email = user[0][1]
        print(email)
        if user_id:
            exists = conn.read(f"SELECT * FROM {today} WHERE user_id = {user_id}")
            if len(exists) == 0:
                try:
                    conn.insert(f"INSERT INTO {today} VALUES(%s, %s, %s, %s)", (name, user_id, email, current_time))
                except Exception as e:
                    print(e)
    else:
        print(f"No user found with name {name}")


@app.get("/download_attendance", response_class=StreamingResponse)
async def download_attendance():
    results = extract_attendance()

    def iter_csv():
        file = StringIO()
        writer = csv.writer(file)
        writer.writerow(["ID", "Name", "Email", "Time"])
        for row in results:
            writer.writerow(row)
            yield file.getvalue()
            file.seek(0)
            file.truncate(0)

    return StreamingResponse(iter_csv(), media_type="text/csv",
                             headers={"Content-Disposition": f"attachment; filename=attendance_{today}.csv"})



def identify_person():
    video_capture = cv2.VideoCapture(0)
    video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    skip_frames = 2  # Skip every 2 frames
    frame_count = 0

    try:
        while True:
            ret, frame = video_capture.read()

            if frame_count % skip_frames == 0:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_locations = face_recognition.face_locations(rgb_frame)
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

                for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                    matches = face_recognition.compare_faces(known_faces, face_encoding)
                    name = 'Unknown'

                    if True in matches:
                        matched_indices = [i for i, match in enumerate(matches) if match]
                        for index in matched_indices:
                            name = known_names[index]
                            print(name)
                            mark_attendance(name)

                            # Draw rectangle around the face
                            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

                            # Draw the name on the rectangle
                            font = cv2.FONT_HERSHEY_DUPLEX
                            cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

                cv2.imshow('Camera', frame)

                key = cv2.waitKey(1)

                if key == ord('q'):
                    break

            frame_count += 1

    finally:
        video_capture.release()
        cv2.destroyAllWindows()
        for i in range(5):
            cv2.waitKey(1)


@app.get("/", response_class=JSONResponse)
async def home(request: Request):
    conn.create(f"CREATE TABLE IF NOT EXISTS {today} (name VARCHAR(30), user_id INT, email VARCHAR(30), time VARCHAR(10))")
    userDetails = extract_attendance()
    get_known_encodings()
    response_data = {
        "request_info": {
            "client": str(request.client),
            "method": request.method,
            "url": request.url.path,
            "query_params": dict(request.query_params),
        },
        "data": {
            "l": len(userDetails),
            "today": today.replace("_", "-"),
            "totalreg": totalreg(),
            "userDetails": userDetails,
        }
    }
    return JSONResponse(content=response_data)


@app.get("/video_feed", response_class=JSONResponse)
async def video_feed():
    identify_person()
    response = RedirectResponse(url='http://localhost:3000')
    return response


@app.post("/add_user", response_class=JSONResponse)
async def add_user(request: Request, newusername: str = Form(...), email: str = Form(...)):
    name = newusername
    userimagefolder = 'static/faces'
    if not os.path.isdir(userimagefolder):
        os.makedirs(userimagefolder)
    video_capture = cv2.VideoCapture(0)
    video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while True:
        ret, frame = video_capture.read()
        flipped_frame = cv2.flip(frame, 1)

        text = "Press Q to Capture & Save the Image"

        font = cv2.FONT_HERSHEY_COMPLEX
        font_scale = 0.9

        font_color = (0, 0, 200)

        thickness = 2

        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        text_x = (frame.shape[1] - text_size[0]) // 2
        text_y = (frame.shape[0] - 450)

        cv2.putText(flipped_frame, text, (text_x, text_y), font, font_scale, font_color, thickness, cv2.LINE_AA)

        cv2.imshow('Camera', flipped_frame)

        key = cv2.waitKey(1)
        if key == ord('q'):
            img_name = name + '.jpg'
            cv2.imwrite(userimagefolder + '/' + img_name, flipped_frame)
            image = userimagefolder + '/' + img_name
            conn.insert(f"INSERT INTO users (name, email, image) VALUES(%s, %s, %s)", (name, email, image))
            video_capture.release()
            cv2.destroyAllWindows()
            break

    video_capture.release()
    cv2.destroyAllWindows()
    for i in range(5):  # maybe 5 or more
        cv2.waitKey(1)
    get_known_encodings()
    response = RedirectResponse(url='http://localhost:3000')
    return response

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("attendanceSystem:app", host='0.0.0.0', port=5000, reload=True)
