import json

def load_config():
    try: 
        f = open("zone.json", "r")
        config = json.loads(f.read())
        f.close()
        return True, config
    except:
        return False, None

def save_config(zone_config_dict):
    try: 
        f = open("zone.json", "w")
        f.write(str(zone_config_dict).replace("'", "\""))
        f.close()
        
        return True, zone_config_dict
    except:
        return False, None
