import os
import argparse
import time
import json
import cv2
import face_recognition
import numpy as np

def find_quadrant_position(quantity, height, width, rectangle_left, rectangle_top, rectangle_height, rectangle_width):
    left_position = rectangle_left + (rectangle_width/2)
    top_position = rectangle_top + (rectangle_height/2)

    if quantity == 2 or quantity == 3: # Left
        if left_position < width/3:
            return 0
        if quantity == 3 and (left_position > width/3 and left_position < (width/3) * 2): # Center
            return 1
        if left_position > (width/3) * 2: # Right
            if quantity == 2:
                return 1
            elif quantity == 3:
                return 2
    if left_position > width/3 and left_position < (width/3) * 2 and quantity == 2:
        return 1

    if quantity == 4:
        if top_position < height/2 and left_position < width/2: # Top left
            return 0
        if top_position < height/2 and left_position > width/2: # Top right
            return 1
        if top_position > height/2 and left_position < width/2: # Bottom left
            return 2
        if top_position > height/2 and left_position > width/2: # Bottom right
            return 3

def camera_img_issue(image_path, face_found, similar_faces, multi_faces):
    camera_report_text = "\n \t {\"image\": {"
    camera_report_text += "\n \t \t \"fileName\": \"" + image_path + "\","
    
    # Face found
    if similar_faces:
        camera_report_text += "\n \t \t \"faceFound\": true,"
    elif face_found:
	    camera_report_text += "\n \t \t \"faceFound\": true,"
    else:
	    camera_report_text += "\n \t \t \"faceFound\": false,"

    # Similar faces
    if similar_faces:
        camera_report_text += "\n \t \t \"similarFaces\": true,"
    else:
        camera_report_text += "\n \t \t \"similarFaces\": false,"

    #Multiple faces
    if multi_faces:
        camera_report_text += "\n \t \t \"moreFacesDetected\": true"
    else:
        camera_report_text += "\n \t \t \"moreFacesDetected\": false"

    camera_report_text += "\n \t }"
    camera_report_text += "\n \t },"

    return camera_report_text

def camera_img_issue(image_path, face_found, similar_faces, multi_faces):
    camera_report_text = "\n \t {\"image\": {"
    camera_report_text += "\n \t \t \"fileName\": \"" + image_path + "\","
    
    # Face found
    if similar_faces:
        camera_report_text += "\n \t \t \"faceFound\": true,"
    elif face_found:
	    camera_report_text += "\n \t \t \"faceFound\": true,"
    else:
	    camera_report_text += "\n \t \t \"faceFound\": false,"

    # Similar faces
    if similar_faces:
        camera_report_text += "\n \t \t \"similarFaces\": true,"
    else:
        camera_report_text += "\n \t \t \"similarFaces\": false,"

    #Multiple faces
    if multi_faces:
        camera_report_text += "\n \t \t \"moreFacesDetected\": true"
    else:
        camera_report_text += "\n \t \t \"moreFacesDetected\": false"

    camera_report_text += "\n \t }"
    camera_report_text += "\n \t },"

    return camera_report_text

def raise_error(path, folder):
    #os.system('python ' + remove_script_path + remove_script + " " + path + " " + folder)
    print("{\n \t \"outputMessage\": \"error\" \n}")

def raise_no_images():
    print("{\n \t \"outputMessage\": \"no images\" \n}")

def raise_succeed():
    print("{\n \t \"outputMessage\": \"succeed\" \n}")


def identify_camera_images(single_folder, objects, detected_faces_person, folder):
    camera_list = []
    array_index = 0


    #Creation of the arrays for the person
    face_session_name = "PersonOfTheSession"

    known_face_encodings = [
        detected_faces_person
    ]
    known_face_names = [
        face_session_name
    ]

    #Order the pictures
    full_camera_report = ' '
    for obj in objects:
        if "camera_" in obj:
            camera_list.append(obj)

    camera_list = sorted(camera_list)

    # Take images 4 by 4
    camera_array = [camera_list[i: i+4] for i in range(0, len(camera_list), 4)]

    #Merge images
    for array_element in camera_array:
        cv_imgs_array = []
        merge_number = 0
        first_array_image = folder + '/' + array_element[0]
        if len(array_element) == 4:
            cv_imgs_array.append(cv2.imread(single_folder + '/' + array_element[0]))
            cv_imgs_array.append(cv2.imread(single_folder + '/' + array_element[1]))
            cv_imgs_array.append(cv2.imread(single_folder + '/' + array_element[2]))
            cv_imgs_array.append(cv2.imread(single_folder + '/' + array_element[3]))
            im_v = cv2.hconcat([cv_imgs_array[0], cv_imgs_array[1]])
            im_h = cv2.hconcat([cv_imgs_array[2], cv_imgs_array[3]])
            im_full = cv2.vconcat([im_v, im_h])
            merge_number = 4

        # Percent by which the image is resized
        scale_percent = 50

        # Calculate the 50 percent of original dimensions
        width = int(im_full.shape[1] * scale_percent / 100)
        height = int(im_full.shape[0] * scale_percent / 100)
        dsize = (width, height)

        # Resize image
        resize_image = cv2.resize(im_full, dsize)

        image_merged_name = single_folder + "/" + 'image_merged.jpg'

        if os.path.exists(image_merged_name):
            os.remove(image_merged_name)

        cv2.imwrite(image_merged_name, resize_image)

        # Recognice all the faces on a merged image with the locations
        face_loaded = face_recognition.load_image_file(image_merged_name)
        face_locations = face_recognition.face_locations(face_loaded)
        face_encodings = face_recognition.face_encodings(face_loaded, face_locations)
        face_names = []


        if (len(face_encodings) < 1 ):
            full_camera_report += camera_img_issue(first_array_image, False, False, False)

        else:
            
            #------------------------------------------------------------------ Start analisis for merge of 4 ------------------------------------------------------------------
            if(merge_number != 4):
                print("Merge different than 4")

            elif merge_number == 4:
                face_found_tl = False # Top left
                face_found_tr = False # Top right
                face_found_bl = False # Bottom left
                face_found_br = False # Bottom right

                similar_face_found_tl = False # Top left
                similar_face_found_tr = False # Top right
                similar_face_found_bl = False # Bottom left
                similar_face_found_br = False # Bottom right

                unknown_found_tl = False # Top left
                unknown_found_tr = False # Top right
                unknown_found_bl = False # Bottom left
                unknown_found_br = False # Bottom right

                multi_face_found_tl = False # Top left
                multi_face_found_tr = False # Top right
                multi_face_found_bl = False # Bottom left
                multi_face_found_br = False # Bottom right

                for face_encoding in face_encodings:
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                    name = "Unknown"

                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]

                    face_names.append(name)

                
                #Validate all the images on the merge 
                for (top, right, bottom, left), name in zip(face_locations, face_names):
                    issue_detected = False
                    similar_faces = False
                    multi_faces = False
                    image_path = ""

                    img_pos = find_quadrant_position(4, height, width, left, top, (bottom-top), (right-left))

                    image_path = single_folder + '/' + array_element[img_pos]
                    image_folder_name = folder + '/' + array_element[img_pos]

                    # For the Top left image
                    if img_pos == 0:
                        if face_found_tl: # Detect multiple faces
                            multi_face_found_tl = True

                        if name == face_session_name: # Detect if the face match with the person
                            similar_face_found_tl = True
                        elif name == 'Unknown': # Detect if the face dont match with the person image
                            unknown_found_tl = True

                        # Face found
                        face_found_tl = True

                    # For the Top right image
                    if img_pos == 1:
                        if face_found_tr: # Detect multiple faces
                            multi_face_found_tr = True

                        if name == face_session_name: # Detect if the face match with the person
                            similar_face_found_tr = True
                        elif name == 'Unknown': # Detect if the face dont match with the person image
                            unknown_found_tr = True

                        # Face found
                        face_found_tr = True
                    

                    # For the Bottom left image
                    if img_pos == 2:
                        if face_found_bl: # Detect multiple faces
                            multi_face_found_bl = True

                        if name == face_session_name: # Detect if the face match with the person
                            similar_face_found_bl = True
                        elif name == 'Unknown': # Detect if the face dont match with the person image
                            unknown_found_bl = True

                        # Face found
                        face_found_bl = True

                    # For the Bottom right image
                    if img_pos == 3:
                        if face_found_br: # Detect multiple faces
                            multi_face_found_br = True

                        if name == face_session_name: # Detect if the face match with the person
                            similar_face_found_br = True
                        elif name == 'Unknown': # Detect if the face dont match with the person image
                            unknown_found_br = True

                        # Face found
                        face_found_br = True
                    
                # Create the error report    
                
                #Top left
                if (not face_found_tl or multi_face_found_tl or not similar_face_found_tl):
                    full_camera_report += camera_img_issue(array_element[0], face_found_tl, similar_face_found_tl, multi_face_found_tl)
                #Top right
                if (not face_found_tr or multi_face_found_tr or not similar_face_found_tr):
                    full_camera_report += camera_img_issue(array_element[1], face_found_tr, similar_face_found_tr, multi_face_found_tr)
                #Bottom left
                if (not face_found_bl or multi_face_found_bl or not similar_face_found_bl):
                    full_camera_report += camera_img_issue(array_element[2], face_found_bl, similar_face_found_bl, multi_face_found_bl)
                #Bottom right
                if (not face_found_br or multi_face_found_br or not similar_face_found_br):
                    full_camera_report += camera_img_issue(array_element[3], face_found_br, similar_face_found_br, multi_face_found_br)
            
            #------------------------------------------------------------------ End analisis for merge of 4 ------------------------------------------------------------------

    return full_camera_report

def identify_face(path, folder):
    bucket_folders=[]

    # output values
    output_no_images = False
    output_process_error = False
    output_succeed = False
    
    bucket_folders.append(folder)

# Face recognition
    for folder_name in bucket_folders:
        single_folder = path + folder_name
        second_image_face_id = None
        
        objects = os.listdir(single_folder)

        if len(objects) < 1:
            report_text = "No images on the folder " + single_folder[:1]
            output_no_images = True

        else:
            report_text = ""
            document_image_found = False
            person_image_found = False
            detected_faces_doc_bool = False
            detected_faces_person_bool = False
            document_pic_name_text = ""
            person_pic_name_text = ""
            
            for obj in objects:
                if ('document_' in obj) or ('verification_document' in obj): # Find the first image and detect the face
                    document_image_found = True
                    document_pic_name = single_folder + "/" + obj
                    document_pic_name_text = folder + "/" + obj
                elif ('person_' in obj) or ('verification_person' in obj): # Find the second image and detect the face
                    person_image_found = True
                    person_pic_name = single_folder + "/" + obj
                    person_pic_name_text = folder + "/" + obj

            
            #Validate Person Image
            second_image_face_ids = None
            if person_image_found:
                report_text += "\"personImage\": {"
                report_text += "\n \t \"fileName\": \"" + person_pic_name_text + "\","
                try:
                    person_img_stream = face_recognition.load_image_file(person_pic_name)
                    detected_faces_person =  face_recognition.face_encodings(person_img_stream)[0]

                    report_text += "\n \t \"faceDetected\": true,"

                    detected_faces_person_bool = True

                    faces = face_recognition.face_locations(person_img_stream, number_of_times_to_upsample=1, model='hog')
                    
                    if (len(faces) > 1):
                        report_text += "\n \t \"moreFacesDetected\": true"
                    else:
                        report_text += "\n \t \"moreFacesDetected\": false"

                    report_text = report_text + "\n },"
                    output_succeed = True

                except IndexError as e:
                    output_process_error = True
                    report_text += "\n \t \"faceDetected\": false"
                    report_text = report_text + "\n },"
            else:
                report_text +="\n \"personImage\": {"
                report_text = report_text + "\n },"


            #Validate Document Image
            if document_image_found:
                report_text +="\n \"documentImage\": {"
                report_text += "\n \t \"fileName\": \"" + document_pic_name_text + "\","
                try:
                    
                    document_img_stream = face_recognition.load_image_file(document_pic_name)
                    detected_faces_doc =  face_recognition.face_encodings(document_img_stream)[0]
                    
                    detected_faces_doc_bool = True

                    report_text +="\n \t \"faceDetected\": true"

                    faces = face_recognition.face_locations(document_img_stream, number_of_times_to_upsample=1, model='hog')

                    report_text = report_text + "\n },"

                except:
                    report_text += "\n \t \"faceDetected\": false"
                    report_text = report_text + "\n },"
                
            else:
                report_text +="{ \n \"documentImage\": {"
                report_text = report_text + "\n },"

            #Validate Person Image VS Document Image
            report_text += "\n \"documentAndPersonValidation\": {"
            if detected_faces_person_bool and detected_faces_doc_bool:
                report_text += "\n \t \"facesDetectedOnBothImages\": true,"

                try:
                    similar_faces = face_recognition.compare_faces([detected_faces_person], detected_faces_doc)
                    
                    if similar_faces[0] == True:
                        report_text += "\n \t \"similarFaces\": true"
                    else:
                        report_text += "\n \t \"similarFaces\": false"
                        

                except:
                    output_process_error = False

            report_text = report_text + "\n },"

            #For all the other picturs look validate
            report_text += "\n \"cameraImages\": ["
            
            if(detected_faces_person_bool):
                report_text += identify_camera_images(single_folder, objects, detected_faces_person, folder)[:-1]

            report_text = report_text + "\n ]"

            report_text = "{ \n " + report_text + "\n }"

            #Transform report text to json
            arr_noface_issue = []
            arr_normal_issue = []
            json_report = json.loads(report_text)
            
            for img_element in json_report['cameraImages']:
                    if img_element['image']['faceFound'] == False:
                            arr_noface_issue.append(img_element)
                    else:
                            arr_normal_issue.append(img_element)

            if len(arr_noface_issue) > 8:
                arr_interval = []
                pos_interval = int(round(1.0 * len(arr_noface_issue) / 8))

                for x in range(0, len(arr_noface_issue) - 1, pos_interval):
                        arr_interval.append(arr_noface_issue[x])

                json_report['cameraImages'] = arr_normal_issue + arr_interval
                json_str = json.dumps(json_report)
                report_text = json_str
            
            print("$$$$$"+report_text+"$$$$$")

    # Output message
    if output_no_images:
        raise_no_images()
    elif output_process_error:
        raise_error(path, folder)
    elif output_succeed:
        raise_succeed()
    
    

def main(path, folder):
    print('Start: ' + time.strftime("%Y %m %d %H %M %S"))
    identify_face(path, folder)
    print('Finish: ' + time.strftime("%Y %m %d %H %M %S"))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Detects faces in the given folder.')
    parser.add_argument('path', help='Path')
    parser.add_argument('folder', help='Folder')
    args = parser.parse_args()
    main(args.path, args.folder)
