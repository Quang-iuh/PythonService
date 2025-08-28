import streamlit as st
import cv2
import time

st.title("🎥 Camera Streaming với OpenCV")

cap = cv2.VideoCapture('http://192.168.1.6:8080/video')

frame_placeholder = st.empty()

while True:
    ret, frame = cap.read()
    if not ret:
        st.write("Không mở được camera")
        break

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    frame_placeholder.image(frame, channels="RGB")

    # Giảm tải CPU (20 fps)
    time.sleep(0.05)

cap.release()
