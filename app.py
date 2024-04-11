from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from ultralytics import YOLO
import cv2
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def count_fish(video_path, model_path, tracker_path):
    model = YOLO(model_path)
    cap = cv2.VideoCapture(video_path)
    total_count = 0

    try:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            results = model.track(frame, tracker=tracker_path, persist=True)
            fish_count = len(results[0].boxes)
            total_count += fish_count

            annotated_frame = results[0].plot()
            cv2.putText(annotated_frame, f"Count: {fish_count}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(annotated_frame, f"Total Count: {total_count}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            #cv2.imshow("YOLOv8 Tracking", annotated_frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            # Remove time.sleep(1) as it might cause the application to hang

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()
    return total_count


# def count_fish(video_path, model_path, tracker_path):
#     model = YOLO(model_path)
#     cap = cv2.VideoCapture(video_path)
#     total_count = []

#     try:
#         while cap.isOpened():
#             success, frame = cap.read()
#             if not success:
#                 break

#             results = model.track(frame, tracker=tracker_path, persist=True)
#             fish_count = len(results[0].boxes)
#             total_count += fish_count
#             total_count.append(fish_count)

#             annotated_frame = results[0].plot()
#             cv2.putText(annotated_frame, f"Count: {fish_count}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
#             #cv2.imshow("YOLOv8 Tracking", annotated_frame)

#             if cv2.waitKey(1) & 0xFF == ord("q"):
#                 break

#     except Exception as e:
#         print(f"An error occurred: {e}")
#     finally:
#         cap.release()
#         cv2.destroyAllWindows()
    
#     return total_count


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/count_fish", methods=["POST"])
def count_fish_route():
    if request.method == "POST":
        if "file" not in request.files:
            return render_template('index.html', message="No file part")

        file = request.files["file"]

        if file.filename == "":
            return render_template("index.html", message="No selected file")

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Perform fish counting on the video
            total_count = count_fish(file_path, "best.pt", "botsort.yaml")

            return render_template('index.html', total_count=[total_count])


# @app.route("/count_fish", methods=["POST"])
# def count_fish_route():
#     if request.method == "POST":
#         if "file" not in request.files:
#             return render_template('index.html', message="No file part")

#         file = request.files["file"]

#         if file.filename == "":
#             return render_template("index.html", message="No selected file")

#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
            
#             if not os.path.exists(app.config['UPLOAD_FOLDER']):
#                 os.makedirs(app.config['UPLOAD_FOLDER'])
            
#             file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             file.save(file_path)

#             # Perform fish counting on the video
#             total_count = count_fish(file_path, "/Users/prathvinrshetty/Desktop/Flask_counting/best.pt", "/Users/prathvinrshetty/Desktop/Flask_counting/botsort.yaml")

#             return render_template('index.html', total_count=total_count)


if __name__=='__main__':
    app.run(host="0.0.0.0", port=5050, debug=True)
