import json
import sys
import requests
import os

def send_runpod_command(command):

  #print(f"\n\n\nSending command: {command}")
  
  runpod_api_key = os.environ.get('RUNPOD_API_KEY')
  if runpod_api_key == None:
    print("")
    quit("Please set your API key, for example like this\n\nexport RUNPOD_API_KEY=...\n")

  runpod_api_url = f"https://api.runpod.io/graphql?api_key={runpod_api_key}"
  #print(runpod_api_url)
  response = requests.post(runpod_api_url, json={'query': command}, headers={})

  if not response.ok:
      print(f"Request failed with status code {response.status_code}")
      print(response.text)
      quit()

  #print(response)
  return(response)

def list_pods():

  command = '''
query Pods {
  myself {
    pods {
      id
      name
      runtime {
        uptimeInSeconds
        ports {
          ip
          isIpPublic
          privatePort
          publicPort
          type
        }
        gpus {
          id
          gpuUtilPercent
          memoryUtilPercent
        }
        container {
          cpuPercent
          memoryPercent
        }
      }
    }
  }
}
'''
  return send_runpod_command(command).json()["data"]["myself"]["pods"]

def terminate_pod(pod_id):
  command = '''
mutation {
  podTerminate(
    input: {
      podId: "%s"
    }
  )
}
  ''' % (pod_id)

  response = send_runpod_command(command)
  return response.status_code


def start_pod(pod_id):
  command = '''
mutation {
  podResume(
    input: {
      podId: "%s",
      gpuCount: 1
    }
  ) {
    id
    desiredStatus
    imageName
    env
    machineId
    machine {
      podHostId
    }
  }
}
  ''' % (pod_id)

  response = send_runpod_command(command)
  return response.status_code


def stop_pod(pod_id):
  command = '''
mutation {
  podStop(
    input: {
      podId: "%s"
    }
  ) {
    id
    desiredStatus
  }
}
  ''' % (pod_id)

  response = send_runpod_command(command)
  return response.status_code



def get_all_pod_ids():
    pods = list_pods()
    return [x["id"] for x in pods]

def terminate_pods(pod_ids):
    for pod_id in pod_ids:
        print(f"Terminating {pod_id}")
        status = terminate_pod(pod_id)
        print(f"status code = {status}")

def start_pods(pod_ids):
    for pod_id in pod_ids:
        print(f"Starting {pod_id}")
        status = start_pod(pod_id)
        print(f"status code = {status}")

def stop_pods(pod_ids):
    for pod_id in pod_ids:
        print(f"Stopping {pod_id}")
        status = stop_pod(pod_id)
        print(f"status code = {status}")

def list_all_pods():
    l = list_pods()
    if (len(l) == 0):
    	print("No pods running at this time")
    else:
    	for pod in l:
    		id = pod["id"]
    		name = pod["name"]
    		runtime = pod["runtime"]
    		#print(json.dumps(l, indent=2))
    		if runtime is not None:
    			uptime = runtime["uptimeInSeconds"]
    			print(f"Pod ID {id} is named >>{name}<< and has been running {uptime} seconds.")
    		else:
    			print(f"Pod ID {id} is named >>{name}<< and is currently not running .")


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python pod_control.py [start|stop|list|terminate] [-ALL|pod_id1 pod_id2 ...]")
        sys.exit()

    command = sys.argv[1]

    if command == "list":
        list_all_pods()
        sys.exit()

    if sys.argv[2] == "-ALL":
        pod_ids = get_all_pod_ids()
    else:
        pod_ids = sys.argv[2:]

    if len(pod_ids) == 0:
        print("No pods to control")
        sys.exit()

    if command == "terminate":
        terminate_pods(pod_ids)
    elif command == "start":
        start_pods(pod_ids)
    elif command == "stop":
        stop_pods(pod_ids)
    else:
        print(f"Invalid command: {command}")
