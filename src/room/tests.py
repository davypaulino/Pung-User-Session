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

from django.test import TestCase, Client
from django.urls import reverse
from django.http import JsonResponse
import json
from .models import Room  # Supondo que Room está no mesmo app

class CreateRoomViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('new-room')  # Insira o nome correto da rota para CreateRoomView

    def test_create_room_success(self):
        data = {
            "createdBy": "user123",
            "roomName": "Test Room",
            "roomType": "1",
            "maxAmountOfPlayers": "4",
            "privateRoom": "true"
        }
        response = self.client.post(self.url, json.dumps(data), content_type="application/json")
        
        # Verifica se o status HTTP é 201 (Created)
        self.assertEqual(response.status_code, 201)
        
        # Verifica o conteúdo da resposta
        response_data = response.json()
        self.assertIn('roomCode', response_data)
        self.assertEqual(response['Location'], f"/session/rooms/{response_data['roomCode']}")
        self.assertEqual(response['userId'], data["createdBy"])

    def test_create_room_missing_fields(self):
        data = {
            "createdBy": "user123",
            "roomName": "Test Room"
            # Faltando roomType e numberOfPlayers
        }
        response = self.client.post(self.url, json.dumps(data), content_type="application/json")
        
        # Verifica se o status HTTP é 400 (Bad Request)
        self.assertEqual(response.status_code, 400)
        
        # Verifica o conteúdo da resposta
        response_data = response.json()
        self.assertEqual(response_data, {'errorCode': '400', 'message': 'Bad Request'})

    def test_create_room_invalid_room_type_format(self):
        data = {
            "createdBy": "user123",
            "roomName": "Test Room",
            "roomType": "invalid",  # Valor inválido
            "maxAmountOfPlayers": "4",
            "privateRoom": "true"
        }
        response = self.client.post(self.url, json.dumps(data), content_type="application/json")
        
        # Verifica se o status HTTP é 400 (Bad Request)
        self.assertEqual(response.status_code, 400)
        
        # Verifica o conteúdo da resposta
        response_data = response.json()
        self.assertEqual(response_data, {'errorCode': '400', 'message': 'Bad Request'})

    def test_create_room_invalid_number_of_players_format(self):
        data = {
            "createdBy": "user123",
            "roomName": "Test Room",
            "roomType": "1",  # Valor inválido
            "maxAmountOfPlayers": "invalid",
            "privateRoom": "true"
        }
        response = self.client.post(self.url, json.dumps(data), content_type="application/json")
        
        # Verifica se o status HTTP é 400 (Bad Request)
        self.assertEqual(response.status_code, 400)
        
        # Verifica o conteúdo da resposta
        response_data = response.json()
        self.assertEqual(response_data, {'errorCode': '400', 'message': 'Bad Request'})
