from django.test import TestCase, Client
from django.urls import reverse
from django.http import JsonResponse
import json
from .models import Room, Player

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

class RoomDetailViewTest(TestCase):
    def setUp(self):
        self.room = Room.objects.create(
            roomCode="12345",
            roomName="Sala Teste",
            roomType=2,
            maxAmountOfPlayers=2,
            privateRoom=False,
            createdBy="Jogador1"
        )

        self.player1 = Player.objects.create(
            roomCode=self.room.roomCode,
            playerId="J1",
            playerName="Jogador1",
            profileColor=1010,
            urlProfileImage="url/template1"
        )
        self.player2 = Player.objects.create(
            roomCode=self.room.roomCode,
            playerId="J2",
            playerName="Jogador2",
            profileColor=2020,
            urlProfileImage="url/template2"
        )
        self.room.amountOfPlayers=2

    def test_get_room_details(self):
        # Simule uma requisição GET à URL da sala com o roomCode
        url = reverse('match', args=[self.room.roomCode])
        response = self.client.get(url)

        # Verifique se a resposta HTTP é 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Verifique se os dados retornados estão corretos
        response_data = response.json()
        
        # Verifique os dados da sala
        self.assertEqual(response_data["roomCode"], self.room.roomCode)
        self.assertEqual(response_data["maxAmountOfPlayers"], self.room.maxAmountOfPlayers)
        self.assertEqual(response_data["amountOfPlayers"], self.room.amountOfPlayers)
        self.assertEqual(response_data["createdBy"], self.room.createdBy)

        # Verifique os dados dos jogadores
        players = response_data["players"]
        self.assertEqual(len(players), 2)

        # Verifique as informações do primeiro jogador
        self.assertEqual(players[0]["playerId"], self.player1.playerId)
        self.assertEqual(players[0]["playerName"], self.player1.playerName)
        self.assertEqual(players[0]["profileColor"], self.player1.profileColor)
        self.assertEqual(players[0]["urlProfileImage"], self.player1.urlProfileImage)

        # Verifique as informações do segundo jogador
        self.assertEqual(players[1]["playerId"], self.player2.playerId)
        self.assertEqual(players[1]["playerName"], self.player2.playerName)
        self.assertEqual(players[1]["profileColor"], self.player2.profileColor)
        self.assertEqual(players[1]["urlProfileImage"], self.player2.urlProfileImage)