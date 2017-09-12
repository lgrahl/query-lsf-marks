"""
A unified cross platform desktop notification tool using *DBus*
or *Growl*.
"""

import enum

# notify2 (DBus)
try:
    import notify2
except ImportError:
    notify2 = None
# gntp (Growl)
if notify2:
    gntp = None
else:
    try:
        import gntp
        import gntp.notifier
    except ImportError:
        gntp = None
# none
if notify2 is None and gntp is None:
    raise ImportError('Install either gntp or notify2 to use this module.')

__all__ = ('NotSupportedError', 'Urgency', 'register', 'Notification')


class NotSupportedError(Exception):
    """
    The type of action is not supported by the specific implementation.

    This error may appear on any method called if
    :attr:`Notification.silent` is not set to `True`.
    """
    pass


class Urgency(enum.IntEnum):
    low = 0
    normal = 1
    high = 2


# TODO: Hints, Actions and Data should be properly supported
# TODO: Handling of stock icons in a cross-platform manner
# TODO: Fix icons in specific implementations and define a way for the base
# implementation
class AbstractNotification:
    """
    A base notification object.

    Arguments:
        - `title`: The title of the notification.
        - `message`: The notification body.
        - `icon`: Path to an icon image or the name of a stock icon.
        - `urgency`: One of the urgency values of :class:`Urgency`.
        - `timeout`: The amount of seconds the notification will be
          displayed. Set to `None` for using the internal default
          value.
        - `silent`: Whether to silently ignore
          :class:`NotSupportedError`s or not.
    """
    def __init__(self, title, message='', icon='', urgency=Urgency.normal, timeout=None,
                 silent=True):
        self._title = title
        self._message = message
        self._icon = icon
        self._urgency = urgency
        self._timeout = timeout
        self._silent = silent

    def show(self):
        """Show the notification."""
        raise NotImplementedError()

    def close(self):
        """Close the notification."""
        raise NotImplementedError()

Notification = AbstractNotification


# noinspection PyUnusedLocal
def register(name):
    """
    Register an application to the notifier.

    .. note:: This function has to be called before notifications
       can be sent.

    Arguments:
        - `name`: The name of the application.
    """
    raise NotImplementedError()


if notify2:
    register = notify2.init

    class Notification(AbstractNotification):
        """
        Adapter for :class:`notify2.Notification`.
        """
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._instance = notify2.Notification(self._title, self._message, self._icon)
            self._instance.set_urgency(self._urgency)  # 1:1 mapping
            if self._timeout is not None:
                self._instance.set_timeout(self._timeout * 1000)  # expects timeout in ms

        def show(self):
            return self._instance.show()

        def close(self):
            return self._instance.close()


if gntp:
    _instance = None

    def _register(name):
        """Sets internal instance."""
        global _instance
        _instance = gntp.notifier.GrowlNotifier(applicationName=name,
                                                notifications=['cross'])
        _instance.register()  # registering required before sending

    register = _register

    class Notification(AbstractNotification):
        """
        Adapter for :class:`gntp.notifier.GrowlNotifier`.
        """
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._instance = _instance
            if self._timeout is not None and self._timeout != 0 and not self._silent:
                raise NotSupportedError("Timeout can't be specified for gntp (Growl),"
                                        " only a value of 0 (sticky) is allowed.")

        def show(self):
            urgency = self._map_urgency(self._urgency)
            sticky = self._timeout == 0
            return self._instance.notify(
                'cross', self._title, self._message, icon=self._icon,
                priority=urgency, sticky=sticky
            )

        def close(self):
            return self._instance.close()

        def callback(self, func):
            return self._instance.connect('closed', func)

        @staticmethod
        def _map_urgency(urgency):
            return (urgency * 2) - 2
