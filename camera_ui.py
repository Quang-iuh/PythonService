import cv2

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Đặt độ phân giải cho camera
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("Không thể mở camera.")
else:
    print("Camera đã được mở thành công. Nhấn 'q' để thoát.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Không thể đọc frame.")
            break

        cv2.imshow('Camera Feed', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()