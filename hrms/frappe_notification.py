import requests
import frappe

class FrappeNotification:
    CENTRAL_SERVER_ENDPOINT = "http://notification.relay:8000"
    PROJECT_NAME = ""
    SITE_NAME = ""
    API_KEY = ""
    API_SECRET = ""

    def __init__(self) -> None:
        raise NotImplementedError

    @staticmethod
    def set_site_name(site_name: str) -> None:
        FrappeNotification.SITE_NAME = site_name

    @staticmethod
    def set_project(project_name: str) -> None:
        FrappeNotification.PROJECT_NAME = project_name

    @staticmethod
    def set_credential(api_key: str, api_secret: str) -> None:
        FrappeNotification.API_KEY = api_key
        FrappeNotification.API_SECRET = api_secret

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
            headers = {
                "Authorization": f"token {FrappeNotification.API_KEY}:{FrappeNotification.API_SECRET}"
            }
            print(headers)
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
