from django.shortcuts import render
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import base64
from PIL import Image,ImageFont,ImageDraw
import io
from io import BytesIO

import time
import face_recognition
import numpy as np
from ams.models import Attendance,e2csecse2
from django.db import connections
from datetime import datetime
import os
from django.template import loader
g=set()
client=str()
ver=int()
it=int()
@csrf_exempt
def home(request):
    template=loader.get_template('index.html')
    return HttpResponse(template.render())

@csrf_exempt
def identify(request):
    global ver
    if request.method == 'POST':
        data=json.loads(request.body)
        image_data =data["image_data"]

        if image_data:
            # decode the base64 encoded image data
            image_data = base64.b64decode(image_data.split(',')[1])
            np=Image.open(BytesIO(image_data))

            IMAGE =np.rotate(90, expand=True)
            # IMAGE.show()
            with BytesIO() as output:
                IMAGE.save(output, format='PNG')
                image_bytes = output.getvalue()
            IMAGE = BytesIO(image_bytes)

            
            MODEL = 'hog'  # 'hog' or 'cnn'
            #constants declaration
            TOLERANCE = 0.5
            # ROOT_DIR = '/content/drive/MyDrive/AMS_MINI_PROJECT'
            FONT = ImageFont.truetype('./arial.ttf', 16)
            # IMAGE="d.jpg"

            image = face_recognition.load_image_file(IMAGE)
            if max(image.shape) > 1600:
                pil_img = Image.fromarray(image)
                pil_img.thumbnail((1600, 1600), Image.LANCZOS)
                image = np.array(pil_img)
            else:
                print("some error")
            pil_image = Image.fromarray(image)
            draw = ImageDraw.Draw(pil_image)
            locations = face_recognition.face_locations(image, model=MODEL)
            encodings = face_recognition.face_encodings(image, locations)
            md=data["data"]
            strg=md["class"]+md["branch"]+md["section"]+".json"
            
            with open("./models/"+strg,"r") as f:
                global total
                dat=json.load(f)
                known_faces=dat["known_faces"]
                
                total=set(known_faces.keys())
            findings=set()
            for face_encoding, face_location in zip(encodings, locations):
                match=None
                for i in known_faces:
                    
                    results = face_recognition.compare_faces(known_faces[i], face_encoding, TOLERANCE)
                    per=0
                    if (len(results)!=0):
                        per=results.count(True)/len(results)
                    top, right, bottom, left = face_location
                    if (per>=0.5):      
                        draw.rectangle(((left, top), (right, bottom)), outline='green', width=2)
                        draw.text((left+6, top-20), i, font=FONT, fill='green')
                        
                        findings.add(i)
                        match=True
                        break
                if (match==None):
                    draw.rectangle(((left, top), (right, bottom)), outline='red', width=2)
                    draw.text((left+6, top-20), "unknown", font=FONT, fill='red')
            global g
            idb=list(findings.difference(g))
            g.update(findings)
            client=list(total.difference(g))          
            date=datetime.now().strftime("%Y%m%d")
            col=""
            q=""
            q2=""
            print(len(findings),"",len(total),"",len(g))

            print("idb is",idb)
            if (len(idb)>=1):
                for i in idb:
                    print(i)
                    col+=f"{i},"
                    q+=f"'1',"
                    q2+=f"{i}='1',"
                print("query is "+q2+"\n"+col)
                print(client)
                del draw
                buffer = io.BytesIO()
                pil_image.save(buffer, format='JPEG')
                reply = base64.b64encode(buffer.getvalue())
                cur=connections["seconddb"].cursor()
                
                table=md["class"]+md["branch"]+md["section"]
                cur.execute(f"select date from {table} where date={date}")
                if(len(cur.fetchall())==0):
                    print(f"insert into {table}('date,'{col[0:-1]}) values('{date}','{q[0:-1]}) ")
                    cur.execute(f"insert into {table}(date,{col[0:-1]}) values('{date}',{q[0:-1]}) ")
                else:
                    print(f"update {table} set {q2[0:-1]} where date='{date}' ")
                    cur.execute(f"update {table} set {q2[0:-1]} where date='{date}'")

#             if (strg=="E1csecse1.json"):
#                 db=Attendance(date=datetime.now().strftime("%Y%m%d"),N181022=data["N181022"],N180924=data["N180924"],N180825=data["N180825"],N180789=data["N180789"],N170976=data["N170976"])
#                 db.save()
#             elif(strg=="E2csecse2.json"):
#                 db=e2csecse2(date=datetime.now().strftime("%Y%m%d"),N200037= data["N200037"],
#  N200377= data["N200377"],
#  N200381= data["N200381"],
#  N200392= data["N200392"],
#  N200491= data["N200491"],
#  N200517= data["N200517"],
#  N200539= data["N200539"],
#  N200542= data["N200542"],
#  N200572= data["N200572"],
#  N200575= data["N200575"],
#  N200594= data["N200594"],
#  N200680= data["N200680"],
#  N200689= data["N200689"],
#  N200695= data["N200695"],
#  N200745= data["N200745"],
#  N200770= data["N200770"],
#  N200814= data["N200814"],
#  N200829= data["N200829"],
#  N200841= data["N200841"],
#  N200883= data["N200883"],
#  N200910= data["N200910"],
#  N200947= data["N200947"],
#  N200948= data["N200948"],
#  N200957= data["N200957"],
#  N201006= data["N201006"],
#  N201014= data["N201014"],
#  N201045= data["N201045"],
#  N201050= data["N201050"],
#  N201056= data["N201056"],
#  N201064= data["N201064"],
#  N201070= data["N201070"])
#                 db.save()
                return JsonResponse({"image":"data:image/jpeg;base64,"+reply.decode("utf-8"),"findings":list(g)})
            else:
                return JsonResponse({"image":0})

        else:
            return JsonResponse({"prompt":"not a correct image"})
    # if request.method == 'POST':
    #     data=json.loads(request.body)
    #     image_data =data["image_data"]
    #     if image_data:
    #         # decode the base64 encoded image data
    #         image_data = base64.b64decode(image_data.split(',')[1])
            
    #         # open the image using PIL
    #         img = Image.open(BytesIO(image_data))
            
    #         # display the image in the console
    #         img.show()

    #         return JsonResponse({'message': 'Image displayed successfully.'})
    # return JsonResponse({'error': 'No image data found.'})

@csrf_exempt
def Login(request):
    global client
    from .models import Credentials
    if request.method=='POST':
        data=json.loads(request.body)
        print(data)
        cur=connections['seconddb'].cursor()
        cur.execute(f"select * from credentials where username='{data['username']}' and password={data['password']}")
        check=cur.fetchall()
        cur.close()
        print(len(check))
        if(len(check)==1):
            client=data["username"]
            print("hi")
            return JsonResponse({"Login":1})
        else:
            return JsonResponse({"Login":0})
        
    else:
        return JsonResponse({"Login":"failure"})
@csrf_exempt
def Verify(req):
  global g
  global ver
  g.clear()
  try:
    if req.method == 'POST':
        data=json.loads(req.body)
        # print(len(data))
        
        image_data =data["image_data"]
        if image_data:
            # decode the base64 encoded image data
            image_data = base64.b64decode(image_data.split(',')[1])
            IMAGE =io.BytesIO(image_data)
            MODEL = 'hog'  # 'hog' or 'cnn'
            #constants declaration
            TOLERANCE = 0.5 
            
        
            image = face_recognition.load_image_file(IMAGE)
            locations = face_recognition.face_locations(image, model=MODEL)
            encodings = face_recognition.face_encodings(image, locations)
            
            # print(len(encodings))
         
            with open("./faculty.json","r") as f:
                
                data=json.load(f)
                known_faces=data["known_faces"]
            for face_encoding, face_location in zip(encodings, locations):
                match=None
                print(client)
                results = face_recognition.compare_faces(known_faces[client], face_encoding, TOLERANCE)
                per=0
                print("hi")
                if (len(results)!=0):
                    per=results.count(True)/len(results)
                else:
                    print("sme")
                if (per>=0.5):
                    ver=1
                    return JsonResponse({"verification":1})
                else:
                    
                    return JsonResponse({"verification":0})
            
            

                # return JsonResponse({"image":"data:image/jpeg;base64,"+reply.decode("utf-8"),"findings":findings})
        else:
            return JsonResponse({"verification":0})
    else:
         return JsonResponse({"verification":0})
  except Exception as e:
    print("error is ",e)

@csrf_exempt
def newreg(req):
    try:
    # global ver
        if req.method == 'POST':
            data=json.loads(req.body)
            print(len(data))
            
            image_data =data["image_data"]
            if image_data:
                # decode the base64 encoded image data
                image_data = base64.b64decode(image_data.split(',')[1])
                IMAGE =io.BytesIO(image_data)
                MODEL = 'hog'  # 'hog' or 'cnn'
                #constants declaration
                TOLERANCE = 0.5
                
                md=data["data"]
                ID=md["user"].upper()
                strg=md["class"]+md["branch"]+md["section"]+".json"

                with open("./models/"+strg,"r+") as x:
                    model=json.load(x)
                    global it
                    image = face_recognition.load_image_file(IMAGE)

                    if (it==0):

                        known=list(model["known_faces"].keys())
                        if(md["user"]) not in known:
                            size = os.path.getsize("./models/"+strg)
                            x.seek(size-2,0) 
                            if max(image.shape) > 1600:
                                pil_img = Image.fromarray(image)
                                pil_img.thumbnail((1600, 1600), Image.LANCZOS)
                                image = np.array(pil_img)
                            encoding = face_recognition.face_encodings(image)
                            if(len(encoding)==1):
                                dat='"'+ID+'"'+":"+str([encoding[0].tolist()])
                                t=","+dat+"}}"
                                
                                os.mkdir(os.path.join("pictures",md["class"],md["branch"],md["section"],md["user"]))
                                now = str(datetime.now()).replace(':', '_')
                                Image.fromarray(image).save(os.path.join("pictures",md["class"],md["branch"],md["section"],md["user"],now)+".png")
                                x.write(t)
                                cur=connections["seconddb"].cursor()
                                table=md["class"]+md["branch"]+md["section"]
                                cur.execute(f"alter table {table} add column {md['user']} int(1) default 0 ")
                                it+=1
                                return JsonResponse({"message":1})
                            else:
                                return JsonResponse({"message":"images>1/0 found"})
                        else:
                            return JsonResponse({"message":"already exists"})
                    elif(it<4):
                        if max(image.shape) > 1600:
                            pil_img = Image.fromarray(image)
                            pil_img.thumbnail((1600, 1600), Image.LANCZOS)
                            image = np.array(pil_img)
                        encoding = face_recognition.face_encodings(image)
                        if(len(encoding)==1):
                            model["known_faces"][ID].append(encoding[0].tolist())
                            x.seek(0,0)
                            json.dump(model,x)
                            now = str(datetime.now()).replace(':', '_')
                            Image.fromarray(image).save(os.path.join("./pictures",md["class"],md["branch"],md["section"],md["user"],now)+".png")
                            it+=1
                            return JsonResponse({"message":1,"it":it})                    
                        else:
                            return JsonResponse({"message":"images>1/0 found","it":it})
                    elif(it==4):
                        return JsonResponse({"message":1,"it":4})    
            else:
                return JsonResponse({"message":"no face found"})
    except Exception as e:
        print(e)
        return JsonResponse({"message":"some error"})
@csrf_exempt
def update(req):
   if req.method == 'POST':
        data=json.loads(req.body)
        print(len(data))
        
        image_data =data["image_data"]
        if image_data:
            # decode the base64 encoded image data
            image_data = base64.b64decode(image_data.split(',')[1])
            IMAGE =io.BytesIO(image_data)
            MODEL = 'hog'  # 'hog' or 'cnn'
            #constants declaration
            TOLERANCE = 0.5
            
            md=data["data"]
            ID=md["user"]
            strg=md["class"]+md["branch"]+md["section"]+".json"
            with open("./models/"+strg,"r+") as x:
                model=json.load(x)
                image = face_recognition.load_image_file(IMAGE)
                known=list(model["known_faces"].keys())
                if(ID) in known:
                    if max(image.shape) > 1600:
                        pil_img = Image.fromarray(image)
                        pil_img.thumbnail((1600, 1600), Image.LANCZOS)
                        image = np.array(pil_img)
                    encoding = face_recognition.face_encodings(image)
                    if(len(encoding)==1):
                        model["known_faces"][ID].append(encoding[0].tolist())
                        x.seek(0,0)
                        json.dump(model,x)
                        now = str(datetime.now()).replace(':', '_')
                        Image.fromarray(image).save(os.path.join("./pictures",md["class"],md["branch"],md["section"],md["user"],now)+".png")
                        return JsonResponse({"message":1})                    
                    else:
                        return JsonResponse({"message":"images>1/0 found"})
                else:
                    return JsonResponse({"message":"Try new Registrations"})
        else:
            return JsonResponse({"message":"no face found"})
