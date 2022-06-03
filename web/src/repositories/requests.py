import subprocess
subprocess.__file__
import json
import bcrypt
from flask import Response
from datetime import datetime

import requests

'''
ARQUIVO QUE GERENCIA AS VALIDAÇÕES DAS REQUESTS
DE CADA CLASSE CRIADA NOS MODELS
'''

'''
# Tenta checar se a request tá certa
# se não der, retorna bad request
'''
def handleRequest(collection,body, routeName):
    try:  
      res = checkPostedData(collection,body, routeName)
      return res
    except Exception as e:
      error = Response("Error!  " + str(e),status=400)
      return error
    
    
'''
# Faz as validações de cada resource
# trata dos erros http
'''
def checkPostedData(collection,body, functionName):
  # checa se um dos dois parametros (usr ou pwd) ñ tá no body
  if 'username' not in body or 'password' not in body:
    error = {
      "message": "Error: missing required parameter usr/pwd.",
      "status": 401
    }
    return error
  # Ifs encadeados pra checar qual função é (pq esse python ñ aceita switch)
  if functionName == 'register':
    '''BODY DA RESQUEST 1'''
    usr = body["username"]
    pwd = body["password"].encode('utf-8') # precisa passar com encode utf-8
    '''=================='''
    #encripta password
    hash_pwd = bcrypt.hashpw(pwd, bcrypt.gensalt())
    have_same_data = collection.find_one({'Username': usr})
    # se o user ainda não existir (se não encontrar o mesmo dado no banco), deixa criar
    if not have_same_data:
      '''
        INSERT DO BANCO
      '''
      collection.insert_one({
        "Username":usr,
        "Password":hash_pwd,
        "Balance":0,
        "Transfers":[],
        "Loans":[],
        "Tokens": 10,
        "CreatedAt": datetime.now(),
        "UpdatedAt":""
      })
      retJson = {
      "message":"You successfully signed up!",
      "status": 200
      }
    else:
      retJson = {
       "message":"Error! User already exists.",
       "status": 403
      }
    '''=================='''
    return retJson
  # checa se é a função de detectar a imagem
  elif functionName == 'transfer':
    '''BODY DA RESQUEST 2'''
    usr = body["username"]
    pwd = body["password"]
    target = body["target"]
    trf = body["transfer_value"]
    '''=================='''
    pwd_exists = collection.find_one({'Username': usr})["Password"]
    #se existe um password pra aquele user, é pq ele existe
    if pwd_exists:
      #faz update
      tokens = collection.find_one({'Username': usr})["Tokens"]
      #se o user tiver tokens, deixa passar
      if tokens <= 0:
        retJson = {
          "message":"Error! Not enough tokens.",
          "status": 406
        }
      else:
        result = []
        for col in collection.find({'Username': usr},{"Transfers":1}):
          if col["Transfers"]:
            result.append(col["Transfers"])
        print("RESULT:", result)
        print("TRANSFER:", trf)
        #TODO: FAZER LÓGICA DE TRANSFERENCIA
        usrBalance = int(collection.find_one({'Username': usr})["Balance"]) - trf
        result.append(trf)
        print("TRANSFERS:", trf)
        retJson = float(collection.find_one({'Username': target})["Balance"]) + trf
        tokens = tokens -1
        '''
        UPDATE 1 DO BANCO
        '''
        if usrBalance > 0:
          collection.update_one({'Username': target}, {"$set": {
            "Balance":retJson,
            "UpdatedAt": datetime.now(),
          }})
          collection.update_one({'Username': usr}, {"$set": {
            "Balance":usrBalance,
            "Transfers":result,
            "Tokens": tokens,
            "UpdatedAt": datetime.now(),
          }})
          retJson = {
            "message": f"R$ {trf},00  successfully transfered.",
            "response":f"Balance: R$ {usrBalance},00.",
            "Tokens": tokens,
            "status": 200,
          }
          '''=================='''
        else:
          retJson = {
          "message":"Error! Not enough money to make the transfer.",
          "status": 403
        }
    else:
      retJson = {
      "message":"Error! User or password incorrect.",
      "status": 400
      }

    return retJson
  # checa se é a função que lista os usuarios
  elif functionName == 'get-users':
    '''BODY DA RESQUEST 3'''
    usr = body["username"]
    '''=================='''
    pwd_exists = collection.find_one({'Username': usr})["Password"]
    # se existe um password pra aquele user, é pq ele existe
    if pwd_exists:
      #faz update
      tokens = collection.find_one({'Username': usr})["Tokens"]
      # se o user tiver tokens, deixa passar
      if tokens <= 0:
        retJson = {
          "message":"Error! Not enough tokens.",
          "status": 406
        }
      else:
        tokens = tokens -1
        result = []
        '''
        SELECT DO BANCO
        '''
        for col in collection.find({},{"Username":1, "Img":1, "Tokens":1}):
          result.append({
            "username":col["Username"],
            "img":col["Img"],
            "tokens":col["Tokens"],
          })
        
        retJson = {
          "message":"Data successfully retrieved.",
          "data": result,
          "Tokens": tokens,
          "status": 200,
        }
    else:
      retJson = {
      "message":"Error! User or password incorrect.",
      "status": 400
      }
      '''=================='''
    return retJson

  elif functionName == 'refill':
    '''BODY DA RESQUEST 4'''
    usr = body["username"]
    target=body["target"]
    pwd = body["password"]
    tokens = body["tokens"]
    '''=================='''
    pwd_exists = collection.find_one({'Username': usr})["Password"]
    #se existe um password pra aquele user, é pq ele existe
    if pwd_exists and usr == 'admin':
      '''
        UPDATE 2 DO BANCO
      '''
      collection.update_one({'Username': target}, {"$set": {
        "Tokens": tokens,
        "UpdatedAt": datetime.now(),
      }})
      retJson = {
        "message":"Sentence successfully saved.",
        "Tokens": tokens,
        "status": 200,
      }
    else:
      retJson = {
      "message":"Error! Only admin can refill tokens.",
      "status": 403
      }
    '''=================='''
    return retJson
