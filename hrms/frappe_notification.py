import json

import frappe
from frappe.utils.response import Response
from urllib.parse import urlparse
from frappeclient import FrappeClient

class FrappeNotification:
    CENTRAL_SERVER_ENDPOINT = "https://push-notification-relay.frappe.cloud"
    PROJECT_NAME = ""

    @staticmethod
    def set_project(project_name: str) -> None:
        """
        Set the project name.

        :param project_name:  (str) The name of the project.
        :return:
        """
        FrappeNotification.PROJECT_NAME = project_name

    @staticmethod
    def set_central_server_endpoint(endpoint: str) -> None:
        """
        Set the central relay server endpoint.

        :param endpoint: (str) The endpoint of the central relay server with protocol.
        :return:
        """
        FrappeNotification.CENTRAL_SERVER_ENDPOINT = endpoint

    def add_token(self, user_id: str, token: str) -> tuple[bool, str]:
        """
        Add a token for a user.

        :param user_id: (str) The ID of the user. This should be user's unique identifier.
        :param token: (str) The token to be added.
        :return: tuple[bool, str] First element is the success status, second element is the message.
        """
        isSuccessful, data = self._send_post_request("notification_relay.api.token.add", {
            "user_id": user_id,
            "fcm_token": token
        })
        if isSuccessful:
            return data["success"], data["message"]
        else:
            raise Exception(data)

    def remove_token(self, user_id: str, token: str) -> tuple[bool, str]:
        """
        Remove a token for a user.

        :param user_id: (str) The ID of the user. This should be user's unique identifier.
        :param token: (str) The token to be removed.
        :return: tuple[bool, str] First element is the success status, second element is the message.
        """
        isSuccessful, data =  self._send_post_request("notification_relay.api.token.remove", {
            "user_id": user_id,
            "fcm_token": token
        })
        if isSuccessful:
            return data["success"], data["message"]
        else:
            raise Exception(data)

    def add_topic(self, topic_name: str) -> bool:
        """
        Add a notification topic.

        :param topic_name: (str) The name of the topic.
        :return: bool True if successful, False otherwise.
        """
        isSuccessful, data =  self._send_post_request("notification_relay.api.topic.add", {
            "topic_name": topic_name
        })
        if isSuccessful:
            return data["success"]
        else:
            raise Exception(data["message"])

    # Remove Topic
    def remove_topic(self, topic_name: str) -> bool:
        """
        Remove a notification topic.

        :param topic_name: (str) The name of the topic.
        :return: bool True if successful, False otherwise.
        """
        isSuccessful, data =  self._send_post_request("notification_relay.api.topic.remove", {
            "topic_name": topic_name
        })
        if isSuccessful:
            return data["success"]
        else:
            raise Exception(data)

    def subscribe_topic(self, user_id: str, topic_name: str) -> bool:
        """
        Subscribe a user to a topic.

        :param user_id: (str) The ID of the user. This should be user's unique identifier.
        :param topic_name: (str) The name of the topic. This topic should be already created.
        :return:
        """
        isSuccessful, data =  self._send_post_request("notification_relay.api.topic.subscribe", {
            "user_id": user_id,
            "topic_name": topic_name
        })
        if isSuccessful:
            return data["success"]
        else:
            raise Exception(data)

    # Unsubscribe Topic (User)
    def unsubscribe_topic(self, user_id: str, topic_name: str) -> bool:
        """
        Unsubscribe a user from a topic.

        :param user_id: (str) The ID of the user. This should be user's unique identifier.
        :param topic_name: (str) The name of the topic. This topic should be already created.
        :return: bool True if successful, False otherwise.
        """
        isSuccessful, data =  self._send_post_request("notification_relay.api.topic.unsubscribe", {
            "user_id": user_id,
            "topic_name": topic_name
        })
        if isSuccessful:
            return data["success"]
        else:
            raise Exception(data)

    def send_notification_to_user(self, user_id: str, title: str, content: str, link:str=None, data=None) -> bool:
        """
        Send notification to a user.

        :param user_id: (str) The ID of the user. This should be user's unique identifier.
        :param title: (str) The title of the notification.
        :param content: (str) The body of the notification. At max 1000 characters.
        :param link: (str) The link to be opened when the notification is clicked.
        :param data: (dict) The data to be sent with the notification. This can be used to provide extra information while dealing with in-app notifications.
        :return: bool True if the request queued successfully, False otherwise.
        """
        if data is None:
            data = {}
        if link is not None and link != "":
            data["click_action"] = link
        if len(content) > 1000:
            raise Exception("Content should be at max 1000 characters")
        res = self._send_post_request("notification_relay.api.send_notification.user", {
            "user_id": user_id,
            "title": title,
            "content": content,
            "data": json.dumps(data)
        })
        if res[0]:
            return res[1]["success"]
        else:
            raise Exception(res[1])

    def send_notification_to_topic(self, topic_name: str, title: str, content: str, link:str=None, data=None) -> bool:
        """
        Send notification to a notification topic.

        :param topic_name: (str) The name of the topic. This topic should be already created.
        :param title: (str) The title of the notification.
        :param content: (str) The body of the notification. At max 1000 characters.
        :param link: (str) The link to be opened when the notification is clicked.
        :param data: (dict) The data to be sent with the notification. This can be used to provide extra information while dealing with in-app notifications.
        :return:  bool True if the request queued successfully, False otherwise.
        """
        if data is None:
            data = {}
        if link is not None and link != "":
            data["click_action"] = link
        res = self._send_post_request("notification_relay.api.send_notification.topic", {
            "topic_name": topic_name,
            "title": title,
            "content": content,
            "data": json.dumps(data)
        })
        if res[0]:
            return res[1]["success"]
        else:
            raise Exception(res[1])


    def _get_credential(self) -> tuple[str, str]:
        """
        Register & Get the API key and secret from the central relay server.
        Also store the API key and secret in the database for future use.

        NOTE: This method is private and should not be called directly.

        :return: tuple[str, str] The API key and secret.
        """
        # TODO change the method later,as doctype currently part of hrms app
        credential = frappe.get_doc("Relay Server Credential")
        if credential.api_key != "" and credential.api_secret != ""\
                and credential.api_key is not None and credential.api_secret is not None:
            return credential.api_key, credential.api_secret
        else:
            # Generate new credentials
            token = frappe.generate_hash(length=48)
            # store the token in the redis cache
            frappe.cache().set(f"{self._get_site_name}:notification_auth_tmp_token", token, ex=600)
            body = {
                "endpoint": self._get_site_name,
                "protocol": self._get_site_protocol,
                "port": self._get_site_port,
                "token": token,
                "webhook_route": "/api/method/hrms.frappe_notification.webhook" # TODO change this method later while integrating in framework
            }
            isRequestSuccessful, response = self._send_post_request("notification_relay.api.auth.get_credential", body, False)
            if isRequestSuccessful:
                success = response["success"]
                if not success:
                    raise Exception(response["message"])
                credential.api_key = response["credentials"]["api_key"]
                credential.api_secret = response["credentials"]["api_secret"]
                credential.save(ignore_permissions=True)
                frappe.db.commit()
                return credential.api_key, credential.api_secret
            else:
                raise Exception(response)

    def _send_post_request(self, method: str, params: dict, use_authentication: bool=True):
        """
        Send a POST request to the central relay server.

        NOTE: This method is private and should not be called directly.

        :param method: (str) The method to be called on the central relay server.
        :param params: (dict) The parameters to be sent with the request.
        :param use_authentication: (bool) Whether to use authentication or not.
        :return: tuple[bool, dict] First element is the success status of request, second element is the response data.
        """
        try:
            client = FrappeClient(FrappeNotification.CENTRAL_SERVER_ENDPOINT)
            if use_authentication:
                api_key, api_secret = self._get_credential()
                client.authenticate(api_key, api_secret)
            params["project_name"] = FrappeNotification.PROJECT_NAME
            params["site_name"] = self._get_site_name
            response = client.post_api(method, params)
            return True, response
        except Exception as e:
            return False, str(e)

    # Helper methods to fetch properties
    @property
    def _get_site_name(self) -> str:
        return urlparse(frappe.utils.get_url()).hostname

    @property
    def _get_site_protocol(self) -> str:
        return urlparse(frappe.utils.get_url()).scheme

    @property
    def _get_site_port(self) -> str:
        site_uri = urlparse(frappe.utils.get_url())
        if site_uri.port is not None:
            return str(site_uri.port)
        else:
            return ""

# Webhook which will be called by the central relay server for authentication
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
