import clip
import torch

class Clip:
    def __init__(self, model_path, device="cuda"):
        self.model, self.preprocess = clip.load(model_path, device)
        self.device = device
        

    def run(self, img, classes):
        img_input = self.preprocess(img).unsqueeze(0).to(self.device)
        text_inputs = torch.cat([clip.tokenize(f"a photo of {c}") for c in classes]).to(self.device)

        with torch.no_grad():
            image_features = self.model.encode_image(img_input)
            text_features = self.model.encode_text(text_inputs)

        image_features /= image_features.norm(dim=-1, keepdim=True)
        text_features /= text_features.norm(dim=-1, keepdim=True)
        similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)
        values, indices = similarity[0].topk(min(5, len(classes)))

        return values, indices