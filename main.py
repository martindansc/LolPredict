import settings
import api
import transforms
import model

data = transforms.get_players_match_data(0, 100)
model = model.build(data)