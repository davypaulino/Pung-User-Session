from django.test import TestCase
from django.urls import reverse
from django.http import JsonResponse
from .models import Room

class RoomStatusViewTest(TestCase):
    def setUp(self):
        # Criar uma sala de teste no banco de dados de teste
        self.room = Room.objects.create(roomName='Test Room', roomStatus='2')

    def test_room_status_view_success(self):
        # Fazer uma requisição GET para a view com o ID da sala
        response = self.client.get(reverse('room_status', args=[self.room.id]))

        # Verificar se o status HTTP é 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Verificar se o conteúdo JSON retornado está correto
        self.assertJSONEqual(response.content, {'status': self.room.roomStatus})

    def test_room_status_view_room_does_not_exist(self):
        # Fazer uma requisição GET para uma sala que não existe
        invalid_room_id = self.room.id + "invalid_part"
        response = self.client.get(reverse('room_status', args=[invalid_room_id]))

        # Verificar se a resposta é 404 (Not Found)
        self.assertEqual(response.status_code, 404)
