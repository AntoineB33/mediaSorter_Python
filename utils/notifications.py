from win10toast import ToastNotifier

class Notifier:
    def __init__(self):
        self.toast = ToastNotifier()

    def send_notification(self, title, message, duration=5):
        self.toast.show_toast(title, message, duration=duration)
