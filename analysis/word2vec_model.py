from gensim.models import Word2Vec

# Глобальная переменная для хранения модели
w2v_model = None


def load_model():
    global w2v_model
    if w2v_model is None:
        w2v_model = Word2Vec.load("analysis/model.model")
    return w2v_model
