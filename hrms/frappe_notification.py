import requests
import frappe
from frappe.utils.response import Response

class FrappeNotification:
    CENTRAL_SERVER_ENDPOINT = "https://push-notification-relay.frappe.cloud"
    PROJECT_NAME = ""
    SITE_NAME = ""
    API_KEY = ""
    API_SECRET = ""

    def __init__(self) -> None:
        raise NotImplementedError

    @staticmethod
    def set_project(project_name: str) -> None:
        FrappeNotification.PROJECT_NAME = project_name

    # Add Token (User)
    @staticmethod
    def add_token(user_id: str, token: str) -> tuple:
        res = FrappeNotification._send_post_request("/api/method/notification_relay.api.token.add", {
            "user_id": user_id,
            "fcm_token": token
        })
        if res[0]:
            return res[1]["success"], res[1]["message"]
        else:
            raise Exception(res[1])

    # Remove Token (User)
    @staticmethod
    def remove_token(user_id: str, token: str) -> tuple:
        res = FrappeNotification._send_post_request("/api/method/notification_relay.api.token.remove", {
            "user_id": user_id,
            "fcm_token": token
        })
        if res[0]:
            return res[1]["success"], res[1]["message"]
        else:
            raise Exception(res[1])

    # Add Topic
    def add_topic(topic_name: str) -> bool:
        res = FrappeNotification._send_post_request("/api/method/notification_relay.api.topic.add", {
            "topic_name": topic_name
        })
        if res[0]:
            return res[1]["success"]
        else:
            raise Exception(res[1]["message"])

    # Remove Topic
    @staticmethod
    def remove_topic(topic_name: str) -> bool:
        res = FrappeNotification._send_post_request("/api/method/notification_relay.api.topic.remove", {
            "topic_name": topic_name
        })
        if res[0]:
            return res[1]["success"]
        else:
            raise Exception(res[1])

    # Subscribe Topic (User)
    @staticmethod
    def subscribe_topic(user_id: str, topic_name: str) -> bool:
        res = FrappeNotification._send_post_request("/api/method/notification_relay.api.topic.subscribe", {
            "user_id": user_id,
            "topic_name": topic_name
        })
        if res[0]:
            return res[1]["success"]
        else:
            raise Exception(res[1])

    # Unsubscribe Topic (User)
    @staticmethod
    def unsubscribe_topic(user_id: str, topic_name: str) -> bool:
        res = FrappeNotification._send_post_request("/api/method/notification_relay.api.topic.unsubscribe", {
            "user_id": user_id,
            "topic_name": topic_name
        })
        if res[0]:
            return res[1]["success"]
        else:
            raise Exception(res[1])

    # Send notification (User)
    @staticmethod
    def send_notification_to_user(user_id: str, title: str, content: str) -> bool:
        res = FrappeNotification._send_post_request("/api/method/notification_relay.api.send_notification.user", {
            "user_id": user_id,
            "title": title,
            "content": content
        })
        if res[0]:
            return res[1]["success"]
        else:
            raise Exception(res[1])

    # Send notification (Topic)
    @staticmethod
    def send_notification_to_topic(topic_name: str, title: str, content: str) -> bool:
        res = FrappeNotification._send_post_request("/api/method/notification_relay.api.send_notification.topic", {
            "topic_name": topic_name,
            "title": title,
            "content": content
        })
        if res[0]:
            return res[1]["success"]
        else:
            raise Exception(res[1])

    @staticmethod
    def _send_post_request(route: str, params: dict) -> (bool, dict):
        try:
            FrappeNotification.fetch_credentials_from_notification_relay_server()
            headers = {
                "Authorization": f"token {FrappeNotification.API_KEY}:{FrappeNotification.API_SECRET}"
            }
            body = FrappeNotification._inject_static_info(params)
            response = requests.post(FrappeNotification._create_route(route), params=params, json=body, headers=headers)
            if response.status_code == 200:
                responseJson = response.json()
                return True, responseJson["message"]
            else:
                text = response.text
                return False, {"message": "request failed", "status_code": response.status_code, "error": text}
        except Exception as e:
            return False, {"message": str(e)}

    @staticmethod
    def _create_route(route: str) -> str:
        return FrappeNotification.CENTRAL_SERVER_ENDPOINT + FrappeNotification._format_route(route)

    @staticmethod
    def _format_route(route: str) -> str:
        if not route.startswith("/"):
            route = "/" + route
        if route.endswith("/"):
            route = route[:-1]
        return route

    @staticmethod
    def _inject_static_info(query: dict) -> dict:
        query["project_name"] = FrappeNotification.PROJECT_NAME
        query["site_name"] = FrappeNotification.SITE_NAME
        return query

    @staticmethod
    def fetch_credentials_from_notification_relay_server():
        if FrappeNotification.API_KEY != "" and FrappeNotification.API_SECRET != "":
            return
        # TODO change the method later,as doctype currently part of hrms app
        credential = frappe.get_single("Relay Server Credential")
        if credential.api_key != "" and credential.api_secret != "" and credential.api_key is not None and credential.api_secret is not None:
            FrappeNotification.API_KEY = credential.api_key
            FrappeNotification.API_SECRET = credential.api_secret
            return
        # Generate new credentials
        current_site =  frappe.local.site
        # fetch current port from site_config.json
        is_use_webserver_port = frappe.get_conf(FrappeNotification.SITE_NAME).get("notification_use_webserver_port", 0)
        if is_use_webserver_port == 1 or is_use_webserver_port == "1":
            FrappeNotification.SITE_NAME = f"{current_site}:{frappe.get_conf(FrappeNotification.SITE_NAME).get('webserver_port', 8000)}"
        else:
            FrappeNotification.SITE_NAME = current_site
        route = "/api/method/notification_relay.api.auth.get_credential"
        token = frappe.generate_hash(length=48)
        # store the token in the redis cache
        frappe.cache().set(f"{current_site}:notification_auth_tmp_token", token, ex=600)
        body = {
            "endpoint": FrappeNotification.SITE_NAME,
            "token": token,
            "webhook_route": "/api/method/hrms.frappe_notification.webhook"
        }
        response = requests.post(FrappeNotification._create_route(route), json=body)
        if response.status_code == 200:
            responseJson = response.json()
            success = responseJson["message"]["success"]
            message = responseJson["message"]["message"]
            if not success:
                raise Exception(message)
            credentials = responseJson["message"]["credentials"]
            api_key = credentials["api_key"]
            api_secret = credentials["api_secret"]
            # Set the credentials
            FrappeNotification.API_KEY = api_key
            FrappeNotification.API_SECRET = api_secret
            # TODO: store the credentials in doctype (just for testing)
            credential.api_key = api_key
            credential.api_secret = api_secret
            credential.save(ignore_permissions=True)
        else:
            raise Exception(response.text)
@frappe.whitelist(allow_guest=True, methods=['GET'])
def webhook():
    # check if token found in redis cache
    token = frappe.cache().get(f"{frappe.local.site}:notification_auth_tmp_token")
    response = Response()
    response.mimetype = "text/plain; charset=UTF-8"

    if token is None or token == "":
        response.data = ""
        response.status_code = 401
        return response

    response.data = token
    response.status_code = 200
    return response
