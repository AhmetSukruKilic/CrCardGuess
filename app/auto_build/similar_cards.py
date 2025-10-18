from fastapi import Depends
from database import get_db


def match_similar_cards(db=Depends(get_db)):
	pass

