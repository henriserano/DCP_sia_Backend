from huggingface_hub import snapshot_download

MODELS = [
    {"repo_id": "Jean-Baptiste/camembert-ner", "revision": "main"},
    {"repo_id": "iiiorg/piiranha-v1-detect-personal-information", "revision": "main"},
    {"repo_id": "vicgalle/gliner-small-pii", "revision": "main"},
]

def main():
    for m in MODELS:
        snapshot_download(
            repo_id=m["repo_id"],
            revision=m.get("revision", "main"),
            local_files_only=False,
            ignore_patterns=[
                "*.safetensors.index.json",
                "*.msgpack",
                "*.h5",
                "*.ot",
                "*.onnx",
            ],  # optionnel
        )

if __name__ == "__main__":
    main()