from __future__ import absolute_import, unicode_literals

from celery import shared_task
from interface.models import *
from accounts.models import Coder
from judge.celery import app
from engine import script
import os
import json


def db_store(question, user, result):
    j = Job(question=question, coder=user, status=json.dumps(result))
    j.save()


@app.task
def execute(question, coder, code, lang):
    language = {
        "c": "c",
        "c++": "cpp",
        "java": "java",
        "python2": "py",
        "python3": "py"
    }
    ext = language[lang]
    filename = "test." + ext
    try:
        with open(
                os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             filename), "w+") as file:
            file.write(code)
            file.close()
    except:
        print("Exception")
    f = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    question = Question.objects.get(question_name=question['question_name'])
    user = Coder.objects.get(name = coder['name'])
    testcases = Testcases.objects.filter(question=question)
    if (ext == "c"):
        net_res = []
        for tests in testcases:
            result = script.run_c(f, tests.input_path(), tests.output_path())
            net_res.append(result)
            if (result['code'] == 1):
                break
        db_store(question, user, net_res)
    elif (ext == "cpp"):
        net_res = []
        for tests in testcases:
            result = script.run_cpp(f, tests.input_path(), tests.output_path())
            net_res.append(result)
            if (result['code'] == 1):
                break
        db_store(question, user, net_res)
    elif (ext == "py" and lang == "python3"):
        net_res = []
        for tests in testcases:
            result = script.run_python3(f, tests.input_path(),
                                        tests.output_path())
            net_res.append(result)
            if (result['code'] == 1):
                break
        db_store(question, user, net_res)
    elif (ext == "py" and lang == "python2"):
        net_res = []
        for tests in testcases:
            result = script.run_python2(f, tests.input_path(),
                                        tests.output_path())
            net_res.append(result)
            if (result['code'] == 1):
                break
        db_store(question, user, net_res)
    elif (ext == "java"):
        net_res = []
        for tests in testcases:
            result = script.run_java(f, tests.input_path(),
                                     tests.output_path())
            net_res.append(result)
            if (result['code'] == 1):
                break
        db_store(question, user, result)
    else:
        result = {"code": 3, "message": "Language not supported"}
        db_store(question, user, result)
    # os.remove(f)