import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from api.routing import websocket_urlpatterns  # Import WebSocket URLs

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trip_logger.settings')
django.setup()

# Define ASGI application with WebSockets support
application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),  # Handles HTTP requests
        "websocket": AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)  # WebSocket URL routing
        ),
    }
)
