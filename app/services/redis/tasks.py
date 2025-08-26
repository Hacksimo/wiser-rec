import pickle
from app.services.helpers import compute_interaction_score
from app.services import mf

def process_interaction(inter):
    """
    Worker function to compute score and update the MF model.
    """
    score = compute_interaction_score(
        like=inter["like"],
        watchtime=inter.get("watchtime", 0.0),
        duration=inter["duration"],
        dont_suggest=inter["dont_suggest"],
        comment=inter.get("comentario", "")
    )

    model = mf.get_model()
    if model:
        model.update(inter["user_id"], inter["video_id"], score)
        print(f"[UPDATE] user={inter['user_id']} video={inter['video_id']} score={score}")
        with open("data/mf_model.pkl", "wb") as f:
            pickle.dump(model, f)   # save updated model
            print("Model saved to mf_model.pkl")

    return {
        "user_id": inter["user_id"],
        "video_id": inter["video_id"],
        "score": float(score)
    }