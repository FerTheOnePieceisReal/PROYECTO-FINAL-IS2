import json

from app import db
from app.models import Notification


class NotificationService:

    @staticmethod
    def add_notification(user, name, data):
        db.session.execute(
            user.notifications.delete().where(
                Notification.name == name
            )
        )

        notification = Notification(
            name=name,
            payload_json=json.dumps(data),
            user=user
        )

        db.session.add(notification)
        return notification