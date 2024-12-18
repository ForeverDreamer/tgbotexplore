import os
import json


def load_secret():
    base_dir = os.path.abspath(os.path.join(__file__, "../../"))
    if not os.path.exists(base_dir):
        base_dir = os.path.abspath(os.path.join(__file__, "../"))
    with open(os.path.join(base_dir, 'secret.json'), 'rb') as f:
        return json.load(f)
