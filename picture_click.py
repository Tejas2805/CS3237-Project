import cv2

def click_save_picture(img_num):

    cap = cv2.VideoCapture(0) # video capture source camera (Here webcam of laptop)
    ret,frame = cap.read() # return a single frame in variable `frame`

    while True:

        #print("IN CAMERA WHOOPIEEE: ")
        file_name = 'img' + str(img_num) + '.png'
        cv2.imshow('img1',frame) #display the captured image
        if cv2.waitKey(1) & 0xFF == ord('y'): #save on pressing 'y'
            cv2.imwrite(file_name,frame)
            cv2.destroyAllWindows()
            break

    cap.release()
