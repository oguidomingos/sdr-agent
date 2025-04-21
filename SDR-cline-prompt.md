### Um agente usando os princípios do Langflow, N8N e a Evolution API.


Pela lógica deve ser gerado um webhook, que vai ser associado na Evolution API no evento Message_Upsert. Nesse momento, deve-se tratar os dados que vem do webhook de maneira que recebamos o Nome do Usuário que fez o envio da mensagem, o número de celular formato da maneira padrao 55dddnumero, e o conteúdo da mensagem.

O conteúdo dessa mensagem deve ser enviado a um agente com o prompt que está em SDR-Prompt.md e usando a IA generativa do Google Gemini-2.0-flash. Seria interessante ter um window buffer que armazena conhecimento da sessão.

Após o agente processar a mensagem do usuário, ele deve responder de acordo com os prompts e essa resposta deve ser enviada para o usuário final. O próximo passo é um loop, que novamente aguarda a mensagem do contato para seguir o processo do prompt. Deixo abaixo referência dos fluxos do n8n, e do agente que foi criado de maneira simples no Langflow. Tente replicar essa lógica por favor para o código com fidelidade.



## Langflow Workflow

import requests
url = "http://127.0.0.1:7860/api/v1/run/34abc3cd-27ec-43fc-9fa5-eade2cbe7f22"  # The complete API endpoint URL for this flow

# Request payload configuration
payload = {
    "input_value": "what is my name",  # The input value to be processed by the flow
    "output_type": "chat",  # Specifies the expected output format
    "input_type": "chat"  # Specifies the input format
}

# Request headers
headers = {
    "Content-Type": "application/json"
}

try:
    # Send API request
    response = requests.request("POST", url, json=payload, headers=headers)
    response.raise_for_status()  # Raise exception for bad status codes

    # Print response
    print(response.text)

except requests.exceptions.RequestException as e:
    print(f"Error making API request: {e}")
except ValueError as e:
    print(f"Error parsing response: {e}")
    


## N8N workflow

{
  "name": "SDR AGENT",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "evolution/start",
        "options": {}
      },
      "id": "33e691bd-ecde-4a30-8953-1a3dfc8407b2",
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1.1,
      "position": [
        980,
        100
      ],
      "webhookId": "e3286562-63fc-4e62-96c2-4f9eaa2f9ef1"
    },
    {
      "parameters": {
        "method": "POST",
        "url": "http://host.docker.internal:7860/api/v1/run/015e1d4f-3653-4d38-b9b2-46a65e80e34c",
        "sendQuery": true,
        "queryParameters": {
          "parameters": [
            {
              "name": "stream",
              "value": "false"
            }
          ]
        },
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "input_value",
              "value": "={{ $json.message }}"
            },
            {
              "name": "output_type",
              "value": "chat"
            },
            {
              "name": "input_type",
              "value": "chat"
            }
          ]
        },
        "options": {}
      },
      "name": "Enviar p/ Langflow",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [
        1340,
        180
      ],
      "id": "f05d5f92-2ea9-4a8f-afe1-5ea889e0e2d9"
    },
    {
      "parameters": {
        "assignments": {
          "assignments": [
            {
              "id": "8394c99e-c2d2-49a2-b611-70a69056abd7",
              "name": "whatsappId",
              "value": "={{ $json.body.data.key.remoteJid.split(\"@\")[0] }}",
              "type": "string"
            },
            {
              "id": "2fabed82-3b8d-452c-abe2-9f0be8be7e6b",
              "name": "message",
              "value": "={{ $json.body.data.message.conversation }}",
              "type": "string"
            },
            {
              "id": "c24db056-ab37-4163-bb56-c79ecdc6ff75",
              "name": "name",
              "value": "={{ $json.body.data.pushName }}",
              "type": "string"
            }
          ]
        },
        "options": {}
      },
      "id": "8e4bd516-3836-4fb9-a786-3d5f5080bacb",
      "name": "Edit Fields",
      "type": "n8n-nodes-base.set",
      "typeVersion": 3.3,
      "position": [
        1160,
        100
      ]
    },
    {
      "parameters": {
        "assignments": {
          "assignments": [
            {
              "id": "66baee55-d615-49b8-97b2-6e67c13f497c",
              "name": "aiMessage",
              "value": "={{ $json.outputs[0].outputs[0].results.message.data.text }}",
              "type": "string"
            }
          ]
        },
        "options": {}
      },
      "id": "db729bbf-3ab5-4b01-a4e8-1b71c3487572",
      "name": "Edit Fields1",
      "type": "n8n-nodes-base.set",
      "typeVersion": 3.3,
      "position": [
        1560,
        180
      ]
    },
    {
      "parameters": {
        "fieldToSplitOut": "aiMessage",
        "options": {}
      },
      "id": "37d74274-417b-4511-8921-7fda8003fd15",
      "name": "Split Out",
      "type": "n8n-nodes-base.splitOut",
      "typeVersion": 1,
      "position": [
        1700,
        100
      ]
    },
    {
      "parameters": {
        "resource": "messages-api",
        "instanceName": "teste",
        "remoteJid": "={{ $('Edit Fields').item.json.whatsappId }}",
        "messageText": "={{ $('Edit Fields1').item.json.aiMessage }}",
        "options_message": {}
      },
      "name": "Enviar Resposta WhatsApp",
      "type": "n8n-nodes-evolution-api.evolutionApi",
      "typeVersion": 1,
      "position": [
        2300,
        100
      ],
      "id": "81f7ba3b-5280-48f3-aa77-a1eb55be2e63",
      "credentials": {
        "evolutionApi": {
          "id": "pqkRfihUeQHdn7QR",
          "name": "Evolution account"
        }
      }
    },
    {
      "parameters": {
        "resource": "chat-api",
        "operation": "send-presence",
        "instanceName": "teste",
        "remoteJid": "={{ $('Edit Fields').item.json.whatsappId }}"
      },
      "id": "fb7beaca-7bd4-4f44-8f99-dab543d8a216",
      "name": "Evolution API",
      "type": "n8n-nodes-evolution-api.evolutionApi",
      "typeVersion": 1,
      "position": [
        2080,
        80
      ],
      "credentials": {
        "evolutionApi": {
          "id": "pqkRfihUeQHdn7QR",
          "name": "Evolution account"
        }
      }
    },
    {
      "parameters": {
        "amount": 10
      },
      "id": "28d12dd8-acac-4419-b2d5-d55fc2c62ddb",
      "name": "Wait",
      "type": "n8n-nodes-base.wait",
      "typeVersion": 1.1,
      "position": [
        2000,
        440
      ],
      "webhookId": "087f5a42-6b2f-45ac-8b9b-342b79857504"
    },
    {
      "parameters": {
        "options": {}
      },
      "id": "6866c825-3e8e-42e9-b1b6-ba6827b80ae1",
      "name": "Loop Over Items",
      "type": "n8n-nodes-base.splitInBatches",
      "typeVersion": 3,
      "position": [
        1880,
        20
      ]
    }
  ],
  "pinData": {},
  "connections": {
    "Webhook": {
      "main": [
        [
          {
            "node": "Edit Fields",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Enviar p/ Langflow": {
      "main": [
        [
          {
            "node": "Edit Fields1",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Edit Fields": {
      "main": [
        [
          {
            "node": "Enviar p/ Langflow",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Edit Fields1": {
      "main": [
        [
          {
            "node": "Split Out",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Split Out": {
      "main": [
        [
          {
            "node": "Loop Over Items",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Evolution API": {
      "main": [
        [
          {
            "node": "Enviar Resposta WhatsApp",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Enviar Resposta WhatsApp": {
      "main": [
        [
          {
            "node": "Wait",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Wait": {
      "main": [
        [
          {
            "node": "Loop Over Items",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Loop Over Items": {
      "main": [
        [],
        [
          {
            "node": "Evolution API",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  },
  "active": true,
  "settings": {
    "executionOrder": "v1",
    "saveManualExecutions": true,
    "callerPolicy": "workflowsFromSameOwner"
  },
  "versionId": "675c9779-490c-4135-bd01-2286efaab127",
  "meta": {
    "templateCredsSetupCompleted": true,
    "instanceId": "a8642095cc3220f5ffb4266f7a5d758854006dff0380182a7194bbbdab563124"
  },
  "id": "XuiTjwWM42cmoMK6",
  "tags": []
}

