import cv2
import dlib
import numpy as np
import face_recognition

faceLandmarkDetectorPath = 'model/dogHeadDetector.dat'
faceLandmarkPredictorPath = 'model/landmarkDetector.dat'

detector = dlib.cnn_face_detection_model_v1(faceLandmarkDetectorPath)
predictor = dlib.shape_predictor(faceLandmarkPredictorPath)

class DogFaceRecognize:
    def __init__(self):
        self.knownFaceEncodings = np.load('numpy/known_faces.npy')
        self.knownFaceNames = np.load('numpy/known_names.npy')
    
    def detection(self, imageInput, size=None):
        if isinstance(imageInput, str):
            image = cv2.imread(imageInput)
            if image is None:
                print(f"Failed to load image: {imageInput}")
                return None
        else:
            image = imageInput

        height, width = image.shape[:2]
        targetWidth = 200
        newHeight = int((targetWidth / width) * height)
        resizedImg = cv2.resize(image, (targetWidth, newHeight), interpolation=cv2.INTER_AREA)

        detsLocations = faceLocations(resizedImg)
        faceEncodings = face_recognition.face_encodings(resizedImg, detsLocations)
        
        results = []  # 인식 결과를 담을 리스트
        if not faceEncodings:
            print("No faces detected.")
            return None

        for faceEncoding, location in zip(faceEncodings, detsLocations):
            matches = face_recognition.compare_faces(self.knownFaceEncodings, faceEncoding, tolerance=0.4)
            name = "Unknown"

            faceDistances = face_recognition.face_distance(self.knownFaceEncodings, faceEncoding)
            bestMatchIndex = np.argmin(faceDistances)

            if matches[bestMatchIndex]:
                name = self.knownFaceNames[bestMatchIndex]

            top, right, bottom, left = location
            results.append({
                "name": name,
                "location": [top, right, bottom, left]
            })
            print(f"Face detected at [{top}, {right}, {bottom}, {left}] identified as: {name}")

        return results if results else None

def cssBounder(css, imageShape):
    return max(css[0], 0), min(css[1], imageShape[1]), min(css[2], imageShape[0]), max(css[3], 0)

def rectCss(rect):
    return rect.top(), rect.right(), rect.bottom(), rect.left()

def rawFace(img, numberOfTimesToUpsample=1):
    return detector(img, numberOfTimesToUpsample)

def faceLocations(img, numberOfTimesToUpsample=1):
    return [cssBounder(rectCss(face.rect), img.shape) for face in rawFace(img, numberOfTimesToUpsample)]