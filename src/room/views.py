from django.http import JsonResponse
from django.views import View
from .models import Room

class RoomStatusView(View):
    def get(self, request, roomId):
        try:
            room = Room.objects.get(id=roomId)
            return JsonResponse({'status': str(room.roomStatus)})
        except Room.DoesNotExist:
            return JsonResponse({'errorCode': '404', 'message': 'Room status not found'}, status=404)