import json
import requests
from flask import Flask, request

app = Flask(__name__)

# 配置自己的群机器人的 key
WECHAT_API_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your_key"

def convert_to_wechat_markdown(data):
    status = data['status']
    group_labels = data.get('groupLabels', {})
    common_labels = data.get('commonLabels', {})
    alerts = data.get('alerts', [])

    # Modify the alert title based on the status
    alert_title = f"{status.upper()}告警" if status == 'firing' else "告警已解决"
    
    content = f"# {alert_title}\n"
    content += f"> 告警名称: {group_labels.get('alertname')}\n"
    content += f"> 严重程度: {common_labels.get('severity')}\n\n"

    for alert in alerts:
        annotations = alert.get('annotations', {})
        starts_at = alert.get('startsAt', '') # 获取故障时间
        content += f"#### 告警描述\n> {annotations.get('description')}\n"
        content += f"> 故障时间: {starts_at}\n" # 添加故障时间

    content += f"\n[面板地址](http://dashboard.grafana.com)\n" # 添加面板地址

    return {
        'msgtype': 'markdown',
        'markdown': {'content': content}
    }

@app.route('/proxy', methods=['POST'])
def proxy():
    data = request.json
    wechat_data = convert_to_wechat_markdown(data)
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(WECHAT_API_URL, headers=headers, data=json.dumps(wechat_data))
    return response.text, response.status_code

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

