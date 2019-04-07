# -*- coding: utf-8 -*-

from watson_developer_cloud import NaturalLanguageClassifierV1
from watson_developer_cloud import ToneAnalyzerV3

# function to call NLC classifier
def apiNLCTest(comment_text):
    api_key = "LiI3o53WHaOU02ATKIwKhSQdirvntK1lZUPA6rhdEwCZ"
    workspace_ID = "6deb62x509-nlc-477"

    natural_language_classifier = NaturalLanguageClassifierV1(iam_apikey=api_key)
    # classifier instance
    response = natural_language_classifier.classify(workspace_ID, comment_text)
    result = []
    response_new = response.result
    if "classes" in response_new.keys():
        for predicted_class in response_new["classes"]:
            result.append([predicted_class['class_name'],predicted_class['confidence']])
        return(result)

# function to call tone analyzer
def apiToneTest(comment_text):

    tone_analyzer = ToneAnalyzerV3(
    version='2017-09-21',
    iam_apikey='MODwXhl7pCy1NQonErss_VNVgUmXELmQmKKV02HhxW1u',
    url='https://gateway.watsonplatform.net/tone-analyzer/api')
    # analyzer instance
    tone_analysis = tone_analyzer.tone(
        {'text': comment_text},
        'application/json'
    ).get_result()
    if(len(tone_analysis["document_tone"]["tones"])==0) :
        return ["","No Tone"]
    else:
        return(tone_analysis["document_tone"]["tones"][0]["score"],tone_analysis["document_tone"]["tones"][0]["tone_name"])
