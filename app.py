from flask import Flask, render_template, Response
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

app = Flask(__name__)
bridge = CvBridge()
last_frame = None  # Variable to store the latest frame

def image_callback(msg):
    global last_frame
    # Callback function to handle incoming image messages
    cv_image = bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
    last_frame = cv_image  # Update the last frame

@app.route('/')
def index():
    return render_template('index.html')

def gen():
    rospy.init_node('video_subscriber')
    rospy.Subscriber('/camera/image_raw', Image, image_callback)
    rate = rospy.Rate(10)  # Adjust the rate according to your setup

    while not rospy.is_shutdown():
        global last_frame
        if last_frame is not None:
            ret, jpeg = cv2.imencode('.jpg', last_frame)
            frame = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        rate.sleep()

@app.route('/video_feed')
def video_feed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
