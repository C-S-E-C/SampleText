import asyncio
from websockets.asyncio.server import serve
import websockets.exceptions
import json
import random
from uuid import uuid4
PENDING_PAIRING = {}

def add_pairing_group():
    pass
async def start_pairing(data, websocket):
    if len(PENDING_PAIRING) > 0:
        joinable = 0
        for id in PENDING_PAIRING:
            group = PENDING_PAIRING[id]
            if group['mode'] == data['mode'] and group['battlefield'] == data['battlefield']:
                joinable = 1
                users = group['users']
                tmp = {}
                team_a_len = 0
                team_b_len = 0
                for user in users:
                    if user['team'] == 'A':
                        team_a_len += 1
                    else:
                        team_b_len += 1
                if team_a_len == int(group['mode']):
                    tmp['team'] = 'B'
                elif team_b_len == int(group['mode']):
                    tmp['team'] = 'A'
                else:
                    tmp['team'] = random.choice(['A', 'B'])
                tmp['websocket'] = websocket
                tmp['id'] = len(users)
                tmp['name'] = data['userId']
                users.append(tmp)
                my_id = tmp['id']
                my_team = tmp['team']
                group_id = id
                break
        if joinable:
            await websocket.send(json.dumps({'type': 'paired', 'groupId': group_id, 'myId': my_id, 'myTeam': my_team}))
            for player in PENDING_PAIRING[group_id]['users']:
                await player['websocket'].send(json.dumps({'type': 'add_player', 'playerName': player['userId'], 'playerTeam': player['team']}))
            startable = 0
            while not startable:
                pass
        else:
             add_pairing_group()
    else:
        add_pairing_group()