import cv2
import numpy as np
import math
from imutils.video import FPS
from skimage.draw import line as skline
from datetime import datetime
import argparse

#######################################
OPENCV_OBJECT_TRACKERS = {
    "csrt": cv2.TrackerCSRT_create,
    "kcf": cv2.TrackerKCF_create,
    "boosting": cv2.legacy.TrackerBoosting_create,
    "mil": cv2.TrackerMIL_create,
    "tld": cv2.legacy.TrackerTLD_create,
    "medianflow": cv2.legacy.TrackerMedianFlow_create,
    "mosse": cv2.legacy.TrackerMOSSE_create
}


#######################################
def detect_line(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    kernel_size = 5
    blur_gray = cv2.GaussianBlur(gray, (kernel_size, kernel_size), 0)
    edges = cv2.Canny(blur_gray, 50, 150)

    contour, __ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    return contour


def create_line(image, terulet, step_hor, step_ver):
    for i in range(0, terulet[2], step_ver):
        cv2.line(image, (terulet[0] + i, terulet[1]), (terulet[0] + i, terulet[3] + terulet[1]), (0, 255, 0), 1)
    for i in range(0, terulet[3], step_hor):
        cv2.line(image, (terulet[0], terulet[1] + i), (terulet[2] + terulet[0], terulet[1] + i), (0, 255, 0), 1)

    return image


#######################################
def calculate_box(image, p1, p2):
    box_image = np.copy(image) * 0
    cv2.rectangle(box_image, (p1[0], p1[1]), (p2[0], p2[1]), (0, 255, 0), 2)
    gray = cv2.cvtColor(box_image, cv2.COLOR_BGR2GRAY)
    blur_gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur_gray, 50, 150)

    contour, __ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    m = cv2.moments(contour[0])
    if m["m00"] != 0:
        cx = int(m["m10"] / m["m00"])
        cy = int(m["m01"] / m["m00"])
    else:
        cx, cy = 0, 0

    return cx, cy


#######################################
def remove_duplicates(element_list, element):
    for i in range(len(element_list)):
        if element_list[i][0] == element[0] and abs(element_list[i][1] - element[1]) < 5:
            return True
        elif element_list[i][1] == element[1] and abs(element_list[i][0] - element[0]) < 5:
            return True
    return False


#######################################
def calculate_result(bug_line_image_result, line_image_result):
    alllist = []
    filteredlist = []
    for i in range(0, line_image_result.shape[0]):
        for j in range(0, line_image_result.shape[1]):
            if line_image_result.item(i, j, 0) == 0:
                if bug_line_image_result.item(i, j, 0) == 1:
                    alllist.append([i, j])

    filteredlist.append(alllist[0])
    for i in range(len(alllist)):
        for j in range(len(filteredlist)):
            if alllist[i][0] != filteredlist[j][0] and (not remove_duplicates(filteredlist, alllist[i])):
                filteredlist.append(alllist[i])

    return len(filteredlist)


#######################################
def create_blank(input_image, rgb_color=(0, 0, 0)):
    image = np.copy(input_image) * 0
    color = tuple(reversed(rgb_color))
    image[:] = color

    return image


#######################################
def line_detecter_runner(cap, rotate=False, track="csrt", printresult=False, waitkey=False):
    tracker = OPENCV_OBJECT_TRACKERS[track]()
    fps = initBB = Bug_Line_Image = Line_Image = contours = None
    x = y = w = h = H = result = 0
    firstrun = True
    white = (255, 255, 255)
    framename = "Frame_" + datetime.now().strftime('%H_%M_%S')
    cXcYList = []
    while cap.isOpened():
        ret, frame = cap.read()
        if ret is False:
            cv2.drawContours(Line_Image, contours, -1, (0, 0, 0), 1)
            result = calculate_result(Bug_Line_Image, Line_Image)
            if printresult:
                print(int(math.ceil(result / 2)))
            if waitkey:
                cv2.waitKey(0)
            break
        if rotate:
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        contoursed_image = frame
        ########
        if firstrun:
            (H, W) = frame.shape[:2]
            Bug_Line_Image = create_blank(frame, rgb_color=white)
            Line_Image = create_blank(frame, rgb_color=white)
            firstrun = False
            
        if initBB is not None:
            (success, box) = tracker.update(frame)
            if success:
                (x, y, w, h) = [int(v) for v in box]
                cv2.rectangle(frame, (x, y), (x + w, y + h),
                              (0, 255, 0), 2)
            fps.update()
            fps.stop()
            info = [
                ("Success", "Yes" if success else "No"),
                ("Tracker", track),
                ("FPS", "{:.2f}".format(fps.fps()))
            ]
            for (i, (k, v)) in enumerate(info):
                text = "{}: {}".format(k, v)
                cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            cX, cY = calculate_box(frame, (x, y), (x + w, y + h))
            cv2.circle(contoursed_image, (cX, cY), 7, (255, 255, 255), -1)
            cXcYList.append([cX, cY])
            cv2.drawContours(contoursed_image, contours, -1, (0, 255, 0), 1)

            if len(cXcYList) > 1:
                for idx, c in enumerate(cXcYList):
                    if idx > 0:
                        contoursed_image = cv2.line(contoursed_image, tuple(cXcYList[idx]), tuple(cXcYList[idx]),
                                                    (0, 0, 255), 4)
                        contoursed_image = cv2.line(contoursed_image, tuple(cXcYList[idx - 1]), tuple(cXcYList[idx]),
                                                    (255, 0, 0), 1)
                        rr, cc = skline(cXcYList[idx - 1][1], cXcYList[idx - 1][0], cXcYList[idx][1], cXcYList[idx][0])
                        Bug_Line_Image[rr, cc] = 1

        #######################################
        cv2.imshow(framename, contoursed_image)
        #######################################
        key = cv2.waitKey(1) & 0xFF
        if key == ord("f"):
            contours = detect_line(frame)
            initBB = cv2.selectROI(framename, contoursed_image, fromCenter=False, showCrosshair=True)
            tracker.init(frame, initBB)
            fps = FPS().start()
        if key == ord('q'):
            break
    cap.release()
    return result


def line_creater_runner(cap, rotate=False, track="csrt", printresult=False, waitkey=False, create_lines=False):
    tracker = OPENCV_OBJECT_TRACKERS[track]()
    fps = initBB = Bug_Line_Image = Line_Image = Step_Hor = Step_Ver = initArea = None
    x = y = w = h = H = result = 0
    firstrun = True
    white = (255, 255, 255)
    framename = "Frame_" + datetime.now().strftime('%H_%M_%S')
    cXcYList = []
    while cap.isOpened():
        ret, frame = cap.read()
        if ret is False:
            if create_lines:
                Line_Image = create_line(Line_Image, initArea, Step_Hor, Step_Ver)
                result = calculate_result(Bug_Line_Image, Line_Image)
                if printresult:
                    print(result)
            if waitkey:
                cv2.waitKey(0)
            break
        if rotate:
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        contoursed_image = frame
        ########
        if firstrun:
            (H, W) = frame.shape[:2]
            Step_Ver = W // 10
            Step_Hor = H // 5
            Bug_Line_Image = create_blank(frame, rgb_color=white)
            Line_Image = create_blank(frame, rgb_color=white)
            firstrun = False
        if initBB is None:
            cv2.waitKey(10) #small wait for easy selection <- temporary solution
            cv2.putText(frame, 'To start select press F then select bug and examined area with mouse', (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        if initBB is not None:
            (success, box) = tracker.update(frame)
            if success:
                (x, y, w, h) = [int(v) for v in box]
                cv2.rectangle(frame, (x, y), (x + w, y + h),
                              (0, 255, 0), 2)
            fps.update()
            fps.stop()
            info = [
                ("Success", "Yes" if success else "No"),
                ("Tracker", track),
                ("FPS", "{:.2f}".format(fps.fps()))
            ]
            for (i, (k, v)) in enumerate(info):
                text = "{}: {}".format(k, v)
                cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cX, cY = calculate_box(frame, (x, y), (x + w, y + h))
            cv2.circle(contoursed_image, (cX, cY), 7, (255, 255, 255), -1)
            cXcYList.append([cX, cY])
            if create_lines:
                cv2.putText(frame, 'To adjust squares use W,A,S,D', (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                contoursed_image = create_line(contoursed_image, initArea, Step_Hor, Step_Ver)

            if len(cXcYList) > 1:
                for idx, c in enumerate(cXcYList):
                    if idx > 0:
                        contoursed_image = cv2.line(contoursed_image, tuple(cXcYList[idx]), tuple(cXcYList[idx]),
                                                    (0, 0, 255), 4)
                        contoursed_image = cv2.line(contoursed_image, tuple(cXcYList[idx - 1]), tuple(cXcYList[idx]),
                                                    (255, 0, 0), 1)
                        rr, cc = skline(cXcYList[idx - 1][1], cXcYList[idx - 1][0], cXcYList[idx][1], cXcYList[idx][0])
                        Bug_Line_Image[rr, cc] = 1

        #######################################
        cv2.imshow(framename, contoursed_image)
        #######################################
        key = cv2.waitKey(1) & 0xFF
        if key == ord("f"):
            initBB = cv2.selectROI(framename, contoursed_image, fromCenter=False, showCrosshair=True)
            if create_lines:
                initArea = cv2.selectROI(framename, contoursed_image, fromCenter=False, showCrosshair=True)
            tracker.init(frame, initBB)
            fps = FPS().start()
        if key == ord("s"):
            Step_Hor = Step_Hor + 1
        if key == ord("w"):
            Step_Hor = Step_Hor - 1
        if key == ord("d"):
            Step_Ver = Step_Ver + 1
        if key == ord("a"):
            Step_Ver = Step_Ver - 1
        if key == ord('q'):
            break
    cap.release()
    return result


def main():
    parser = argparse.ArgumentParser(description="Ultimate bug tracking", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("file", help="Path to the video")
    parser.add_argument("-r", "--rotate", action="store_true", help="Rotate the video 90°")
    parser.add_argument("-c", "--create", action="store_true", help="Draw squares")
    parser.add_argument("-d", "--detect", action="store_true", help="Automaticaly detect boundaries")
    parser.add_argument("-p", "--printresult", action="store_false", help="Don't print the number of reached squares to the output")
    parser.add_argument("-w", "--waitkey", action="store_false", help="Don't wait after the video is finished")
    args = parser.parse_args()
    
    Video = cv2.VideoCapture(args.file)

    if args.detect:
        line_detecter_runner(Video, rotate=args.rotate, printresult=args.printresult, waitkey=args.waitkey)
    else:
        line_creater_runner(Video, rotate=args.rotate, printresult=args.printresult, waitkey=args.waitkey, create_lines=args.create)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
