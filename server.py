from flask import Flask,Response,request
import requests
import pymongo
import json
from bson import json_util
import os

app = Flask(__name__)

try:
    #Enter DB credentials
    USERNAME = os.environ.get("USERNAME")
    PASSWORD = os.environ.get("PASSWORD")
    HOST = os.environ.get("HOST")
    PORT = os.environ.get("PORT")

    client = pymongo.MongoClient("mongodb://"+USERNAME+":"+PASSWORD+"@"+HOST+":"+PORT)
   
    db=client["aashish"]

except Exception as ex:
    print(ex)
    print("cannot connect to DB")

@app.route("/store_projects",methods=["POST"])
def store_projects():
    try:
        id=request.form["id"]
        data=requests.get("http://sentenceapi2.servers.nferx.com:8015/tagrecorder/v3/projects/"+str(id))
        json_data=data.json()
        datasets=(json_data['result']['project']['associated_datasets'])
        models=(json_data['result']['project']['models'])
        projects=(json_data['result']['project'])

        
        db.projects.update({"_id":projects["_id"]},projects,upsert=True)

        for model in models:
            db.models.update({"model_name":model["model_name"]},model,upsert=True)
        for dataset in datasets:
            db.datasets.update({"_id":dataset["_id"]},dataset,upsert=True)

        
        return Response(
            response=data,
            status=200, 
            mimetype="application/json"
        )
        
    except Exception as ex:
        print(ex)
        return Response(
            response=json.dumps({"message":"Cannot post data into DB"}),
            status=500, 
            mimetype="application/json"
        )


@app.route("/getinfo",methods=["GET"])
def get_info():
    try:
        infotype=request.args.get("infotype")
        
        if(infotype=="dataset"):
            id=request.args.get("id")
            data = db.datasets.find_one({"_id":id})
            
            return Response(
            response=json.dumps(data),
            status=200, 
            mimetype="application/json"
        )
        if(infotype=="model"):
            model_name=request.args.get("model_name")
            data = db.models.find_one({"model_name":model_name})
            data["_id"] = str(data["_id"])
            return Response(
            response=json.dumps(data),
            status=200, 
            mimetype="application/json"
        )
    except Exception as ex:
        print(ex)
        return Response(
            response=json.dumps({"message":"cannot get model or dataset info"}),
            status=500, 
            mimetype="application/json"
        )

@app.route("/getproject",methods=["GET"])
def get_project():
    try:
        projectid=request.args.get("projectid")
        data = db.projects.find_one({"_id":projectid})
        return Response(
        response=json.dumps(data),
        status=200, 
        mimetype="application/json"
        )
    except Exception as ex:
        print(ex)
        return Response(
            response=json.dumps({"message":"cannot get projects"}),
            status=500, 
            mimetype="application/json"
        )

@app.route("/getmodels",methods=["GET"])
def get_models():
    try:
        datasetid=request.args.get("datasetid")
        datasets = list(db.models.find({"datasets_used.dataset_id":datasetid}))
        return Response(
        response=json.dumps(datasets,default=json_util.default),
        status=200, 
        mimetype="application/json"
        )
    except Exception as ex:
        print(ex)
        return Response(
            response=json.dumps({"message":"cannot get models"}),
            status=500, 
            mimetype="application/json"
        )

if __name__ == "__main__":
    app.run(port=8000,debug=True)



