import streamlit as st
import cv2
import time

st.title("🎥 Camera Streaming với OpenCV")

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

frame_placeholder = st.empty()
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
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
