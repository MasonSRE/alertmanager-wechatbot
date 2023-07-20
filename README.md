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

````shell
# 配置自己的群机器人的 key
WECHAT_API_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your_key"

# 配置自己的 grafana 面板地址
content += f"\n[面板地址](http://dashboard.grafana.com)\n" # 添加面板地址

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
![图片描述](https://github.com/MasonSRE/alertmanager-wechatbot/blob/main/wechatbot.png)
