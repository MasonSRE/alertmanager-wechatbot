## python 告警代理服务器



#### 安装python 环境

```shell
# 安装
yum install -y epel-release
yum install -y python3
yum install -y python3-pip

# 验证
python3 --version
pip3 --version

# 使用pip3来安装 requests 和 flask 库：
pip3 install requests flask
```



#### 编写代理服务器

`main.py`

````python
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

````



#### 启动服务器

```shell
nohup python3 main.py &
```



#### 手动测试

```shell
curl -X POST http://localhost:8000/proxy -H "Content-Type: application/json" -d '{
  "status": "firing",
  "groupLabels": {"alertname": "TestAlert"},
  "commonLabels": {
    "cluster": "TestCluster",
    "service": "TestService",
    "severity": "critical"
  },
  "alerts": [
    {
      "annotations": {
        "description": "This is a test alert."
      }
    }
  ]
}'
```



#### 配置 Alertmanager

```yaml
global:
  resolve_timeout: 5m

route:
  group_by: ['alertname']
  group_wait: 30s          # 初次发送告警延时
  group_interval: 5m      # 距离第一次发送告警，等待多久再次发送告警
  repeat_interval: 24h     # 告警重发时间
  receiver: 'default-receiver'
  routes:
  - match:
      severity: critical
    receiver: 'weixin-receiver'

receivers:
- name: 'default-receiver'
- name: 'weixin-receiver'
  webhook_configs:
  - url: 'http://127.0.0.1:8000/proxy'
    send_resolved: true
```

