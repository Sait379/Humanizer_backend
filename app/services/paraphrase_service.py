from app.repositories.paraphrasing_repo import ParaphrasingRepo

class ParaphraseService:
    def __init__(self):
        self.repo = ParaphrasingRepo()

    def run(self, text: str):
        return self.repo.paraphrase(text)
