import requests
import json
from datetime import datetime, timedelta
import subprocess
import os
import boto3

# Mock monitoring system (replace with Grafana API)
def get_alarms():
    # Simulate getting alarms
    return [
        {
            "service": "microservice",
            "pod": "microservice-123",
            "error": "Secret expired",
            "type": "secret_expiry",
            "timestamp": "2023-10-01T12:00:00Z"
        },
        {
            "service": "microservice",
            "pod": "microservice-123",
            "error": "Config invalid",
            "type": "config_error",
            "timestamp": "2023-10-01T12:05:00Z"
        },
        {
            "service": "microservice",
            "pod": "microservice-123",
            "error": "High CPU",
            "type": "resource_issue",
            "timestamp": "2023-10-01T12:10:00Z"
        },
        {
            "service": "microservice",
            "pod": "microservice-123",
            "error": "DB connection failed",
            "type": "dependency_fail",
            "timestamp": "2023-10-01T12:15:00Z"
        }
    ]

# Query OpenSearch for logs
def query_logs(service, start_time, end_time):
    # Mock query
    logs = [
        {"timestamp": "2023-10-01T11:59:00Z", "message": "Starting service"},
        {"timestamp": "2023-10-01T12:00:00Z", "message": "Secret expired on 2023-09-30"},
        {"timestamp": "2023-10-01T12:05:00Z", "message": "Config error: invalid value invalid"},
        {"timestamp": "2023-10-01T12:10:00Z", "message": "High CPU usage detected"},
        {"timestamp": "2023-10-01T12:15:00Z", "message": "Database connection failed"}
    ]
    return [log for log in logs if start_time <= datetime.fromisoformat(log["timestamp"].replace("Z", "+00:00")) <= end_time]

# Analyze logs with AI (simplified)
def analyze_logs(logs, alarm):
    alarm_type = alarm.get("type", "")
    if alarm_type == "secret_expiry":
        return {"fixable": True, "action": "rotate_secret", "reason": "Secret expired, can rotate"}
    elif alarm_type == "config_error":
        return {"fixable": True, "action": "update_config", "reason": "Config invalid, can update"}
    elif alarm_type == "resource_issue":
        return {"fixable": True, "action": "restart_pod", "reason": "High CPU, restart pod"}
    elif alarm_type == "dependency_fail":
        return {"fixable": True, "action": "restart_dependency", "reason": "DB fail, restart DB"}
    return {"fixable": False}

# Perform fix
def perform_fix(action, alarm):
    if action == "rotate_secret":
        # Use AWS SecretsManager
        client = boto3.client('secretsmanager', region_name='us-east-1')
        # Assume secret name
        client.rotate_secret(SecretId='my-secret')
        print("Rotated secret")
    elif action == "update_config":
        # Update config in GitHub
        # Assume token and repo
        headers = {'Authorization': f'token {os.getenv("GITHUB_TOKEN")}'}
        url = 'https://api.github.com/repos/your-repo/config-file'
        # Get current content, update, put back
        response = requests.get(url, headers=headers)
        content = json.loads(response.json()['content'])  # Assume JSON
        content['key'] = 'valid'
        new_content = json.dumps(content)
        requests.put(url, headers=headers, json={'message': 'Fix config', 'content': new_content})
        print("Updated config")
    elif action == "restart_pod":
        subprocess.run(["kubectl", "delete", "pod", alarm["pod"]])
        print("Restarted pod")
    elif action == "restart_dependency":
        subprocess.run(["kubectl", "delete", "pod", "db-pod"])  # Assume pod name
        print("Restarted dependency")

def main():
    alarms = get_alarms()
    for alarm in alarms:
        start_time = datetime.fromisoformat(alarm["timestamp"].replace("Z", "+00:00")) - timedelta(minutes=5)
        end_time = datetime.fromisoformat(alarm["timestamp"].replace("Z", "+00:00")) + timedelta(minutes=5)
        logs = query_logs(alarm["service"], start_time, end_time)
        analysis = analyze_logs(logs, alarm)
        if analysis["fixable"]:
            perform_fix(analysis["action"], alarm)

if __name__ == '__main__':
    main()