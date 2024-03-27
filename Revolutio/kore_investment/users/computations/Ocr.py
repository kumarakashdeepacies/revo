import cv2
import numpy as np
import pytesseract


def ocr(template_image, uploaded_image, roi):
    imgQ = cv2.imread(template_image)
    h, w, c = imgQ.shape

    orb = cv2.ORB_create(5000)
    kp1, des1 = orb.detectAndCompute(imgQ, None)

    img = cv2.cvtColor(np.array(uploaded_image), cv2.COLOR_RGB2BGR)
    per = 25

    kp2, des2 = orb.detectAndCompute(img, None)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING)
    matches = bf.match(des2, des1)
    matches.sort(key=lambda x: x.distance)
    good = matches[: int(len(matches) * (per / 100))]

    srcPoints = np.float32([kp2[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dstPoints = np.float32([kp1[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

    M, _ = cv2.findHomography(srcPoints, dstPoints, cv2.RANSAC, 5.0)
    imgScan = cv2.warpPerspective(img, M, (w, h))

    myPoints = roi.values()

    imgShow = imgScan.copy()

    imgMask = np.zeros_like(imgShow)
    myData = {}
    for x, r in enumerate(myPoints):
        r[0][0] = int(r[0][0])
        r[0][1] = int(r[0][1])
        r[1][0] = int(r[1][0])
        r[1][1] = int(r[1][1])
        cv2.rectangle(imgMask, (r[0][0], r[0][1]), (r[1][0], r[1][1]), (0, 255, 0), cv2.FILLED)
        imgShow = cv2.addWeighted(imgShow, 0.99, imgMask, 0.1, 0)
        imgCrop = imgScan[r[0][1] : r[1][1], r[0][0] : r[1][0]]

        result = imgCrop.copy()
        gray = cv2.cvtColor(imgCrop, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        # Find vertical lines
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 15))
        detect_vertical = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
        cnts = cv2.findContours(detect_vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        for c in cnts:
            cv2.drawContours(result, [c], -1, (255, 255, 255), -1)

        imgCrop = result.copy()
        length_x, width_y, c = imgCrop.shape
        factor = min(1, float(1024.0 / length_x))
        size = int(factor * width_y), int(factor * length_x)
        imgCrop = cv2.resize(imgCrop, size)

        kernel = np.ones((1, 1), np.uint8)
        opening = cv2.morphologyEx(imgCrop, cv2.MORPH_OPEN, kernel)
        closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
        imgCrop = cv2.bitwise_or(imgCrop, closing)

        if r[2] == "text":
            myData[r[3]] = (pytesseract.image_to_string(imgCrop, config="-psm 6")).strip()

        cv2.putText(
            imgShow, str(myData[r[3]]), (r[0][0], r[0][1]), cv2.FONT_HERSHEY_PLAIN, 2.5, (0, 0, 255), 4
        )

    return myData
