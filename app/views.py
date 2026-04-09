import cv2
from django.shortcuts import render
from .forms import ImageForm
from .models import ImageUpload
import os
import mediapipe as mp

def overlay_saree(person_path, saree_path, output_path):
    person = cv2.imread(person_path)
    saree = cv2.imread(saree_path)

    landmarks = detect_body_points(person)

    if landmarks is None:
        cv2.imwrite(output_path, person)
        return

    h, w, _ = person.shape

    # Get shoulder points
    left_shoulder = landmarks[11]
    right_shoulder = landmarks[12]

    x1 = int(left_shoulder.x * w)
    x2 = int(right_shoulder.x * w)
    y = int(left_shoulder.y * h)

    saree_width = abs(x2 - x1) + 100
    saree_height = int(h * 0.8)

    saree = cv2.resize(saree, (saree_width, saree_height))

    x_offset = min(x1, x2) - 50
    y_offset = y

    # safety
    x_offset = max(0, x_offset)
    y_offset = max(0, y_offset)

    end_x = min(x_offset + saree.shape[1], w)
    end_y = min(y_offset + saree.shape[0], h)

    saree = saree[0:end_y-y_offset, 0:end_x-x_offset]
    roi = person[y_offset:end_y, x_offset:end_x]

    gray = cv2.cvtColor(saree, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    mask_inv = cv2.bitwise_not(mask)

    person_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)
    saree_fg = cv2.bitwise_and(saree, saree, mask=mask)

    dst = cv2.add(person_bg, saree_fg)
    person[y_offset:end_y, x_offset:end_x] = dst

    cv2.imwrite(output_path, person)
def upload_image(request):
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save()

            person_path = obj.person_image.path
            saree_path = obj.saree_image.path

            output_filename = 'result_' + str(obj.id) + '.jpg'
            output_path = os.path.join('media/output/', output_filename)

            overlay_saree(person_path, saree_path, output_path)

            obj.output_image = 'output/' + output_filename
            obj.save()

            return render(request, 'result.html', {'obj': obj})
    else:
        form = ImageForm()

    return render(request, 'upload.html', {'form': form})


mp_pose = mp.solutions.pose

def detect_body_points(image):
    with mp_pose.Pose(static_image_mode=True) as pose:
        results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        if results.pose_landmarks:
            return results.pose_landmarks.landmark
        return None