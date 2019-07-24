import json
import requests
import boto3

def darksky():
    latitude = "35.685175"
    longitude = "139.7528"
    apikey = "dc9c..."
    url = "https://api.darksky.net/forecast/{0}/{1},{2}".format(apikey, latitude, longitude)

    try:
        r = requests.get(url, timeout=5)
        r = r.json()
        if "daily" in r:
            precip_prob = r["daily"]["data"][0]["precipProbability"]
            precip_prob = round(precip_prob * 100)
            return precip_prob
        else:
            error_code = r["code"]
            error = r["error"]
            return str(error_code) + error

    except requests.exceptions.RequestException as e:
        e = str(e)
        e = e[:160] #SMSの上限が160文字なのでエラーメッセージを先頭160文字でカット
        return e

def slack_post(msg):
    url = "https://hooks.slack.com/services/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" #Webhook URL
    payload = {
        "username": "お天気通知BOT",
        "text": msg
    }
    requests.post(url, data=json.dumps(payload))


def awssns_post(msg):
    client = boto3.client(
        "sns",
        aws_access_key_id="AKI...", #アクセスキー
        aws_secret_access_key="eG/...", #シークレットキー
        region_name="ap-northeast-1" #リージョン https://docs.aws.amazon.com/ja_jp/sns/latest/dg/sms_supported-countries.html
    )

    client.publish(
        PhoneNumber="+818000000000", #電話番号(国番号付き)
        Message=msg
    )

#AWS Lambdaを利用するときは、以下の行を「def lambda_handler(event, context):」等として関数定義して実行
probability = darksky()

if isinstance(probability, str) or probability > 49: #文字列だと数字の比較ができないので先にisinstanceを書く
    if isinstance(probability, int):
        probability = "傘を持って出かけてください（今日の降水確率は{}%です）".format(probability)
    slack_post(probability)
    awssns_post(probability)
