# pipeline/emb_linker.py
from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

def _flatten_vocab(vocab):
    texts, meta = [], []
    for item in vocab:
        for lab in item["labels"]:
            texts.append(lab)
            meta.append(item)
    return texts, meta

class OntologyLinker:
    def __init__(self, classes, obj_props, data_props, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

        self.cls_texts, self.cls_meta  = _flatten_vocab(classes)
        self.op_texts,  self.op_meta   = _flatten_vocab(obj_props)
        self.dp_texts,  self.dp_meta   = _flatten_vocab(data_props)

        self.cls_emb = self.model.encode(self.cls_texts, show_progress_bar=False)
        self.op_emb  = self.model.encode(self.op_texts,  show_progress_bar=False)
        self.dp_emb  = self.model.encode(self.dp_texts,  show_progress_bar=False)

    def link_entity(self, mention: str, top_k=1, threshold=0.55) -> List[Dict[str,Any]]:
        v = self.model.encode([mention])
        sims = cosine_similarity(v, self.cls_emb)[0]
        idx = sims.argsort()[::-1][:top_k]
        out = []
        for i in idx:
            if sims[i] >= threshold:
                out.append({"score": float(sims[i]), **self.cls_meta[i]})
        return out

    def link_property(self, mention: str, top_k=1, threshold=0.55) -> List[Dict[str,Any]]:
        v = self.model.encode([mention])
        sims_op = cosine_similarity(v, self.op_emb)[0]
        sims_dp = cosine_similarity(v, self.dp_emb)[0]

        i1 = sims_op.argsort()[::-1][:top_k]
        i2 = sims_dp.argsort()[::-1][:top_k]

        cand = []
        for i in i1:
            if sims_op[i] >= threshold:
                cand.append({"score": float(sims_op[i]), "kind":"object", **self.op_meta[i]})
        for i in i2:
            if sims_dp[i] >= threshold:
                cand.append({"score": float(sims_dp[i]), "kind":"data", **self.dp_meta[i]})
        cand.sort(key=lambda x: -x["score"])
        return cand[:top_k]
